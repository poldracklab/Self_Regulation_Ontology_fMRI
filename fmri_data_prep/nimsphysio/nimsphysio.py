#!/usr/bin/env python
#
# @author:  Bob Dougherty
# (Note that the regressor computation code was mostly transcribed from Catie Chang's
# Matlab implementation of retroicor_rvhr.)

"""
The CNI physiological data procesor. Takes physio data (cardiac and respiration),
cleans it to be synchronous with the scan, and computes retroicor and rvhrcor regressors.
See:

* Glover GH, Li TQ, Ress D. Image-based method for retrospective correction of
  physiological motion effects in fMRI: RETROICOR. Magn Reson Med. 2000 Jul;44(1):162-7.
  PubMed PMID: 10893535

* Chang C, Cunningham JP, Glover GH. Influence of heart rate on the BOLD signal:
  the cardiac response function. Neuroimage. 2009 Feb 1;44(3):857-69. doi:
  10.1016/j.neuroimage.2008.09.029. Epub 2008 Oct 7. PubMed PMID: 18951982
"""

import gzip
import json
import logging
import nibabel as nib
from nibabel.spatialimages import HeaderDataError
import tarfile
import zipfile
import argparse
import datetime
import warnings
import itertools
import numpy as np
from scipy.stats import zscore
from bson import loads as bloads # modified for new bson syntax

import os
import sys

from . import nimsdata  # modified from original to use local nimsdata

log = logging.getLogger('nimsphysio')


class NIMSPhysioError(nimsdata.NIMSDataError):
    pass


class NIMSPhysio(nimsdata.NIMSReader):
    """
    Read and process physiological data recorded during an MR scan.

    This class reads the physio data and generates RETROICOR and RETORVHR
    regressors from the data.

    Takes either a list of the physio files or a filename that points to a
    zip or tgz file containing the files.

    If tr and/or nframes are missing, the data will not be properly time-shifted
    to the start of the scan and the regressors won't be valid.

    Ideally, you should specify the slice_order, in which case, num_slices can be
    omitted since it will be inferred from the slice_order list. If you don't,
    the code will assume a standard interleaved acquisition. If neither slice_order
    nor num_slices is specified, the regressors can't be computed.

    Example:
        import physio
        p = physio.PhysioData(filename='physio.zip', tr=2, nframes=120, nslices=36)
        p.generate_regressors(outname='retroicor.csv')
    """
    domain = 'mr'
    filetype = 'gephysio'
    parse_priority = 7
    required_metadata_fields = ['group', 'experiment', 'session', 'epoch', 'timestamp']
    state = ['orig']

    # TODO: simplify init to take no args. We need to add the relevant info to the json file.
    def __init__(self, filenames, tr=2, nframes=100, slice_onsets=None, slice_window=None, card_dt=0.01, resp_dt=0.04):
        # does not use super(NIMSPhysio, self).__init__(filename) because nimsphysio expects a LIST of inputs
        self._schema_init(self.project_properties)
        self._schema_init(self.session_properties)
        self._schema_init(self.acquisition_properties)
        self.data = None
        self.metadata_status = 'empty'

        # The is_valid method uses some crude heuristics to detect valid data.
        # To be valid, the number of temporal frames must be reasonable, and either the cardiac
        # standard deviation or the respiration low-frequency power meet the following criteria.
        self.min_number_of_frames = 8
        self.min_card_std = 4.
        self.min_resp_lfp = 40.
        # FIXME: How to infer the file format automatically?
        self.format_str = 'ge'
        self.tr = float(tr)
        self.nframes = nframes
        self.slice_onsets = slice_onsets  # Significant Change ---------------
        self.slice_window = slice_window
        if slice_window is None:
            windows = np.diff(sorted(set(slice_onsets)))
            if len(windows): # if slice timing corrected, all slices occur at 0, no difference
                assert all(np.allclose(x, windows[0]) for x in windows), \
                    'appears that there is variability in the gap between slice onsets, please provide a window.'
                self.slice_window = windows[0] 
            else:
                self.slice_window = 0  # Significant Change ---------------
        self.card_wave = None
        self.card_trig = None
        self.card_dt = float(card_dt)
        self.card_time = None
        self.heart_rate = None
        self.resp_wave = None
        self.resp_trig = None
        self.resp_dt = float(resp_dt)
        self.resp_time = None
        self.regressors = None
        self.phases = None
        self.scan_duration = (self.nframes or 1) * self.tr
        self.exam_uid = ''
        self.series_uid = ''
        self.series_no = ''
        self.acq_no = ''
        #self.subj_firstname = None
        #self.subj_lastname = None
        #self.subj_dob = None
        #self.subj_sex = None
        try:
            if self.format_str=='ge':
                self.read_ge_data(filenames)
            else:
                raise NIMSPhysioError('only GE physio format is currently supported')
                # insert other vendor's read_data functions here
        except Exception as e:
            raise NIMSPhysioError(e)

    def read_ge_data(self, filename):
        archive = None
        if isinstance(filename, str):  # modified for python 3 - HJ
            with open(filename, 'rb') as fp:
                magic = fp.read(4)
            if magic in ['\x50\x4b\x03\x04', b'PK\x03\x04']:  # HJ
                archive = zipfile.ZipFile(filename)
                files = [(fn, archive.open(fn)) for fn in archive.namelist()]
            elif magic[:2] == '\x1f\x8b':
                archive = tarfile.open(filename, 'r:*')
                files = [(fn, archive.extractfile(archive.getmember(fn))) for fn in archive.getnames()]
            else:
                raise NIMSPhysioError('only tgz and zip files are supported')
        else:
            files = [(fn, open(fn)) for fn in filename] # assume that we were passed a list of filenames
        for fn, fd in files:
            for substr, attr in (
                    ('RESPData', 'resp_wave'),
                    ('RESPTrig', 'resp_trig'),
                    ('PPGData', 'card_wave'),
                    ('PPGTrig', 'card_trig'),
                    ):
                if substr in fn:
                    with warnings.catch_warnings():
                        warnings.simplefilter('ignore')
                        setattr(self, attr, np.loadtxt(fd))
                    break
            else:
                if fn.endswith('_physio.json'):
                    metadata = bloads(fd)  # modified for new bson syntax - HJ
                    for f in self.required_metadata_fields:
                        if f not in metadata:
                            raise NIMSPhysioError('incomplete json file')
                    for attribute, value in metadata.iteritems():
                        if isinstance(value, datetime.datetime):
                            value = value.replace(tzinfo=None)
                        setattr(self, attribute, value)
        if archive:
            archive.close()

        if (self.resp_wave is not None) and (self.card_wave is not None):  # modified for py3 - HJ
            # move time zero to correspond to the start of the fMRI data
            offset = self.resp_dt * self.resp_wave.size - self.scan_duration
            self.resp_time = self.resp_dt * np.arange(self.resp_wave.size) - offset

            offset = self.card_dt * self.card_wave.size - self.scan_duration
            self.card_time = self.card_dt * np.arange(self.card_wave.size) - offset
            self.card_trig = self.card_trig * self.card_dt - offset
            self.hr_instant = 60. / np.diff(self.card_trig)

    @classmethod
    def derived_metadata(cls, orig_metadata):
        return {f: getattr(orig_metadata, 'nims_'+f) for f in cls.required_metadata_fields}

    def load_data(self):
        pass

    @property
    def nims_metadata_status(self):
        return self.metadata_status

    @property
    def nims_group_id(self):
        return self.group

    @property
    def nims_project(self):
        return self.experiment

    @property
    def nims_session_id(self):
        return self.session

    @property
    def nims_session_label(self):
        pass

    @property
    def nims_session_subject(self):
        pass

    @property
    def nims_acquisition_id(self):
        return self.epoch

    @property
    def nims_acquisition_description(self):
        pass

    @property
    def nims_acquisition_label(self):
        return '%d.%d' % (self.series_no, self.acq_no) if self.acq_no is not None else str(self.series_no)

    @property
    def nims_type(self):
        return ('original', 'physio', self.filetype)

    @property
    def nims_file_name(self):
        return self.nims_epoch + '_' + self.filetype

    @property
    def nims_file_ext(self):
        return ''

    @property
    def nims_file_domain(self):
        return self.domain

    @property
    def nims_file_type(self):
        return self.filetype

    @property
    def nims_file_kinds(self):
        return ['resp', 'ecg']

    @property
    def nims_file_state(self):
        pass

    @property
    def nims_type(self):
        return ('original', 'physio', self.filetype)

    @property
    def nims_timestamp(self): # FIXME: should return UTC time and timezone
        return self.timestamp.replace(tzinfo=bson.tz_util.FixedOffset(-7*60, 'pacific')) #FIXME: use pytz

    @property
    def nims_timezone(self):
        return None

    @property
    def card_trig_chopped(self):
        # find the first trigger that is >0
        start_ind = np.argmax(self.card_trig>0)
        return self.card_trig[start_ind:]

    @property
    def resp_wave_chopped(self):
        start_ind = np.argmax(self.resp_time>0)
        return self.resp_wave[start_ind:]

    def compute_regressors(self, legacy_rvhr=False, hr_min=30, hr_max=180):
        """
         * catie chang,   catie.chang@nih.gov
         * bob dougherty, bobd@stanford.edu

         * 2011.12.13: original matlab implementation (catie)
         * 2012.02.14: modified from retroicor_main.m. This version
           optionally includes RVHRcor regressors too! (RV*RRF, HR*CRF,
           + time derivatives). (catie, feeling the love)
         * 2012.12.14: translated to Python (bob)

         See the following for background:
         Glover et al., 2000: MRM 44, 162-167.
         Birn et al., 2006: Neuroimage 31, 1536-1548.
         Chang et al., 2009: Neuroimage 47, 1448-1459 (appendix A)
         Chang et al., 2009: Neuroimage 44, 857-869

         ---------------------------
         INPUTS:
         ---------------------------
         legacy_rvhr: True to use Catie's original algorithm for computing heartrate,
                      false to use Bob's algorithm, which should be more robust.
         hr_min, hr_max: For Bob's heartrate algorithm, heartrate values outside this
                         range will be discarded. (Has no effect if legacy_rvhr=True)

         The following are set as instance vars:
         * slice order:  vector indicating order of slice acquisition
             (e.g. [30 28 26, .... 29 27 ... 1] for 30 "interleaved down" slices)
         * tr: in seconds
         * nframes: number of frames in the timeseries
         * card_trig: vector of cardiac (R-wave peak) times, in seconds.
         * resp_wave: respiration amplitude signal
         * resp_dt: sampling interval between the points in respiration
             amplitude signal (in seconds, e.g. resp_dt=0.04 for 25 Hz sampling)

          (** setting card_trig = [] will ignore cardiac in both corrections)
          (** setting resp_wave = [] will ignore respiration in both corrections)

         ---------------------------
         OUTPUTS:
         ---------------------------
         * self.phases: list of cardiac & respiration phases for each slice (numpy arrays).
              phases[i,:,0] contains the cardiac phase for slice "i" and
              phases[i,:,1] contains the resp phases for slice "i".
         * self.regressors: retroicor & rvhrcor regressors as [#timepoints x #regressors x #slices].
              I.e., the regressors for slice "i" are the columns of REGRESSORS[:,:,i].
         *
        """
        import scipy.stats
        import scipy.signal

        if self.nframes < 3:
            self.regressors = None
            log.warning('Need at least 3 temporal frames to compute regressors!')
            return

        resp_wave = self.resp_wave_chopped
        card_trig = self.card_trig_chopped

        t_win = 6 * 0.5 # 6-sec window for computing RV & HR, default
        nslc = len(self.slice_onsets)

        # Find the derivative of the respiration waveform
        # shift to zero-min
        resp_wave = resp_wave - resp_wave.min()
        # bin respiration signal into 100 values
        Hb,bins = np.histogram(resp_wave, 100)
        # calculate the derivative
        # first, filter respiratory signal - just in case
        f_cutoff = 1. # max allowable freq
        fs = 1. / self.resp_dt
        wn = f_cutoff / (fs / 2)
        ntaps = 20
        b = scipy.signal.firwin(ntaps, wn)
        respfilt = scipy.signal.filtfilt(b, [1], resp_wave)
        drdt = np.diff(respfilt)

        # --------------------------------------------------------------
        # find cardiac and respiratory phase vectors
        # --------------------------------------------------------------
        self.phases = np.zeros((nslc, self.nframes, 2))
        for sl in range(nslc):
            # times (for each frame) at which this slice was acquired (midpoint):
            # significant shange --------------
            slice_times = np.arange(self.slice_onsets[sl]+(self.slice_window/2), self.scan_duration, self.tr)
            # significant shange --------------
            for fr in range(self.nframes):
                # cardiac
                prev_trigs = np.nonzero(card_trig < slice_times[fr])[0]
                t1 = 0. if prev_trigs.size == 0 else card_trig[prev_trigs[-1]]
                next_trigs = np.nonzero(card_trig > slice_times[fr])[0]
                if next_trigs.size == 0:
                    t2 = self.nframes*self.tr
                else:
                    t2 = card_trig[next_trigs[0]]
                phi_cardiac = (slice_times[fr] - t1) * 2. * np.pi / (t2 - t1)

                # respiration: (based on amplitude histogram)
                # find the closest index in resp waveform
                iphys = int(np.min((np.max((0, np.round(slice_times[fr] / self.resp_dt))), drdt.size-1)))  # HJ
                amp = resp_wave[iphys]
                dbins = np.abs(amp-bins)
                thisBin = dbins.argmin()  #closest resp_wave histo bin
                numer = Hb[0:thisBin].sum().astype(float)
                phi_resp = np.pi * np.sign(drdt[iphys]) * (numer / respfilt.size)

                # store
                self.phases[sl,fr,:] = [phi_cardiac, phi_resp]

        # --------------------------------------------------------------
        # generate slice-specific retroicor regressors
        # --------------------------------------------------------------
        REGRESSORS_RET = np.zeros((self.nframes, 8, nslc))
        for sl in range(nslc):
            phi_c = self.phases[sl,:,0]
            phi_r = self.phases[sl,:,1]

            # Fourier expansion of cardiac phase
            c1_c = np.cos(phi_c)
            s1_c = np.sin(phi_c)
            c2_c = np.cos(2*phi_c)
            s2_c = np.sin(2*phi_c)

            # Fourier expansion of respiratory phase
            c1_r = np.cos(phi_r)
            s1_r = np.sin(phi_r)
            c2_r = np.cos(2*phi_r)
            s2_r = np.sin(2*phi_r)
            covs = np.array((c1_c, s1_c, c2_c, s2_c,c1_r, s1_r, c2_r, s2_r))

            REGRESSORS_RET[:,:,sl] = covs.transpose()

        # --------------------------------------------------------------
        # generate slice-specific rvhrcor regressors
        # --------------------------------------------------------------
        REGRESSORS_RVHR = np.zeros((self.nframes, 4, nslc))
        self.heart_rate = np.zeros((self.nframes, nslc))
        t = np.arange(0, 40-self.tr, self.tr) # 40-sec impulse response
        for sl in range(nslc):
            # times (for each frame) at which this slice was acquired (midpoint):
            # significant change --------
            slice_times = np.arange(self.slice_onsets[sl]+(self.slice_window/2), self.scan_duration, self.tr)
            # significant change --------
            # make slice RV*RRF regressor
            rv = np.zeros(self.nframes)
            for tp in range(self.nframes):
                i1 = int(max(0, np.floor((slice_times[tp] - t_win) / self.resp_dt)))  # HJ
                i2 = int(min(resp_wave.size, np.floor((slice_times[tp] + t_win) / self.resp_dt))) # HJ
                if i2 < i1:
                    raise NIMSPhysioError('Respiration data is shorter than the scan duration.')
                rv[tp] = np.std(resp_wave[i1:i2])

            # conv(rv, rrf)
            rv -= rv.mean()
            R = 0.6 * (t**2.1) * np.exp(-t/1.6) - 0.0023 * (t**3.54) * np.exp(-t/4.25)
            R = R / R.max()
            rv_rrf = np.convolve(rv, R)[0:rv.size]
            # time derivative
            rv_rrf_d = np.diff(rv_rrf)
            rv_rrf_d = np.concatenate(([rv_rrf_d[0]], rv_rrf_d))

            # make slice HR*CRF regressor
            # Catie's original code:
            if legacy_rvhr:
                hr = np.zeros(self.nframes)
                for tp in range(self.nframes):
                    inds = np.nonzero(np.logical_and(card_trig >= (slice_times[tp]-t_win), card_trig <= (slice_times[tp]+t_win)))[0]
                    if inds.size < 2:
                        hr[tp] = 60 if tp==0 else hr[tp-1]
                    else:
                        hr[tp] = (inds[-1] - inds[0]) * 60. / (card_trig[inds[-1]] - card_trig[inds[0]])  # bpm
            else:
                # Bob's new version:
                trig_time_delta = np.diff(card_trig)
                hr_instant = 60. / trig_time_delta
                hr_time = card_trig[:-1] + trig_time_delta / 2.
                # Clean a bit. We interpolate below, so it's safe to just discard bad values.
                keep_inds = np.logical_and(hr_instant>=hr_min, hr_instant<=hr_max)
                hr_time = hr_time[keep_inds]
                hr_instant = hr_instant[keep_inds]
                if len(hr_instant) > 2:
                    hr = np.interp(slice_times, hr_time, hr_instant)
                else:
                    hr = np.zeros(slice_times.shape)

            # conv(hr, crf)
            self.heart_rate[:,sl] = hr
            hr -= hr.mean()
            H = 0.6 * (t**2.7) * np.exp(-t/1.6) - 16 * scipy.stats.norm.pdf(t, 12, 3)
            H /= H.max()
            hr_crf = np.convolve(hr,H)[0:hr.size]
            # time derivative
            hr_crf_d = np.diff(hr_crf)
            hr_crf_d = np.concatenate(([hr_crf_d[0]], hr_crf_d))
            REGRESSORS_RVHR[:,:,sl] = np.array((rv_rrf, rv_rrf_d, hr_crf, hr_crf_d)).transpose()

        # --------------------------------------------------------------
        # final set of physio regressors
        # --------------------------------------------------------------
        self.regressors = np.concatenate((REGRESSORS_RET, REGRESSORS_RVHR, self.heart_rate[:,np.newaxis,:]), axis=1)
        for sl in range(nslc):
            x = np.arange(self.regressors.shape[0]).transpose()
            for reg in range(self.regressors.shape[1] - 1):
                self.regressors[:,reg,sl] -= np.polyval(np.polyfit(x, self.regressors[:,reg,sl], 2), x)


    def denoise_image(self, d, regressors):
        """
        correct the image data: slice-wise
        FIXME: NOT TESTED
        """
        nslc = d.shape[2]
        self.nframes = d.shape[3]
        npix_x = d.shape[0]
        npix_y = d.shape[1]
        PCT_VAR_REDUCED = np.zeros((npix_x,npix_y,nslc))
        d_corrected = np.zeros(d.shape)
        for jj in range(nslc):
            slice_data = np.squeeze(d[:,:,jj,:])
            Y_slice = slice_data.reshape((npix_x*npix_y, self.nframes)).transpose() #ntime x nvox
            t = np.arange(self.nframes)[:, np.newaxis] #  shape=(nTRs, 1)  - HJ
            # design matrix
            # XX = np.array((t, t**2., regressors[:,:,jj]))  # HJ
            XX = np.hstack([t, t**2, regressors[:,:,jj]])  # HJ
            XX = np.hstack([np.ones((XX.shape[0],1)), zscore(XX, 0)])  # HJ
            Betas = np.matmul(np.linalg.pinv(XX), Y_slice)  # HJ
            Y_slice_corr = Y_slice - np.matmul(XX[:,3:-1], Betas[3:-1,:]) # modified by HJ, swapping out * for matmul
            # calculate percent variance reduction  - modified by HJ to make axis and ddof explicit
            var_reduced = (np.var(Y_slice, axis=0, ddof=1) - np.var(Y_slice_corr, axis=0, ddof=1)) / np.var(Y_slice, axis=0, ddof=1)
            PCT_VAR_REDUCED[:,:,jj] = var_reduced.transpose().reshape((npix_x, npix_y))
            # fill corrected volume
            V_slice_corr = Y_slice_corr.transpose()
            for ii in range(self.nframes):
                d_corrected[:,:,jj,ii] = V_slice_corr[:,ii].reshape((npix_x,npix_y))
        return d_corrected, PCT_VAR_REDUCED

    def write_regressors_legacy(self, filename):
        self.compute_regressors()
        # Write the array to disk
        # Thanks to Joe Kington on StackOverflow (http://stackoverflow.com/questions/3685265/how-to-write-a-multidimensional-array-to-a-text-file)
        with file(filename, 'w') as outfile:
            # Write a little header behind comments
            # Any line starting with "#" will be ignored by numpy.loadtxt
            outfile.write('# slice_onests = [ %s ]\n' % ','.join(str(d) for d in self.slice_onsets))
            outfile.write('# Full array shape: {0}\n'.format(self.regressors.shape))
            outfile.write('# time x regressor for each slice in the acquired volume\n')
            outfile.write('# regressors: [ %s ]\n' % ','.join(self.regressor_names))
            for i in range(self.regressors.shape[2]):
                outfile.write('# slice %d\n' % i)
                # Format as left-justified columns 7 chars wide with 2 decimal places.
                np.savetxt(outfile, self.regressors[:,:,i], fmt='%-7.6f')

    def _write_regressors(self, fileobj, header_notes=''):
        # Write a little header behind comments
        # Any line starting with "#" will be ignored by numpy.loadtxt
        fileobj.write('#slice_onsets = [ %s ]\n' % ','.join(str(d) for d in self.slice_onsets))
        if header_notes:
            fileobj.write('#' + header_notes + '\n')
        # print out all the column headings:
        nslices = len(self.slice_onsets)
        fileobj.write('#' + ','.join(h[0]+h[1] for h in itertools.product(['slice'+str(s) for s in range(nslices)], self.regressor_names)) + '\n')
        new_shape = (self.regressors.shape[0], self.regressors.shape[1]*self.regressors.shape[2])
        np.savetxt(fileobj, self.regressors.reshape(new_shape, order='F'), fmt='%0.5f', delimiter=',')
        #d = {key: value for (key, value) in sequence}
        #d['slice_order'] = self.slice_order
        #with file(filename, 'w') as outfile:
        #    json.dump(d, outfile)

    def write_regressors(self, filename):
        """ Save the regressors in a simple csv format file. If the filename ends with .gz, the file will be gzipped. """
        self.compute_regressors()
        if filename.endswith('.gz'):
            with gzip.open(filename, 'wb') as fp:
                self._write_regressors(fp)
        else:
            with open(filename, 'w') as fp:  # HJ
                self._write_regressors(fp)

    def write_raw_data(self, filename):
        """ Save the raw physio data in a json file. If the filename ends with .gz, the file will be gzipped. """
        d = {'resp_time':self.resp_time.round(3).tolist(), 'resp_wave':self.resp_wave.astype(int).tolist(), 'resp_trig':self.resp_trig.round(3).tolist(),
             'card_time':self.card_time.round(3).tolist(), 'card_wave':self.card_wave.astype(int).tolist(), 'card_trig':self.card_trig.round(3).tolist()}
        if filename.endswith('.gz'):
            with gzip.open(filename, 'wb') as fp:
                json.dump(d, fp)
        else:
            with file(filename, 'w') as fp:
                json.dump(d, fp)

    @property
    def regressor_names(self):
        return ('c1_c', 's1_c', 'c2_c', 's2_c', 'c1_r', 's1_r', 'c2_r', 's2_r', 'rv_rrf', 'rv_rrf_d', 'hr_crf', 'hr_crf_d', 'hr')

    def is_valid(self, resp_freq_cutoff=1.0):
        if self.nframes < self.min_number_of_frames or self.resp_wave==None or self.card_wave==None:
            return False
        # Heuristics to detect invalid data
        # When not connected, the PPG output is very low amplitude noise
        hr_instant = 60. / np.diff(self.card_trig)
        proportion_good_hr = np.sum(np.logical_and(hr_instant>=30, hr_instant<=200)) / float(len(hr_instant))
        card_valid = self.card_wave.std() > self.min_card_std and proportion_good_hr>0.2
        # The respiration signal is heavily low-pass filtered, but valid data should still
        # have much more low-frequency energy
        freq = np.abs(np.fft.rfft(self.resp_wave))
        fs = 1. / (self.resp_dt*self.resp_wave.shape[0])
        f_bin = int(round(resp_freq_cutoff/fs))
        if f_bin<freq.size:
            # Look at the ratio of low-frequency amplitudes to high-frequency amplitudes.
            # There should be a lot more low-frequency in there for valid data.
            resp_valid = freq[2:f_bin].mean()/freq[-f_bin:].mean() > self.min_resp_lfp
        else:
            resp_valid = False
        return card_valid or resp_valid


class ArgumentParser(argparse.ArgumentParser):

    def __init__(self):
        super(ArgumentParser, self).__init__()
        self.description = """ Processes physio data to make them amenable to retroicor."""
        self.add_argument('--physio_file', help='path to physio data')
        self.add_argument('--outbase', help='basename for output files')
        self.add_argument('-n', '--nifti_file', help='path to corresponding nifti file')
        # TODO: allow tr, nframes, and nslices to be entered as args if no nifti is provided
        # TODO: allow user to specify custom slice orders
        self.add_argument('-p', '--preprocess', action='store_true', help='Also save pre-processed physio data')
        self.add_argument('--slice_window', default=None, help='include slice window (in s) for corrected data')


if __name__ == '__main__':
    args = ArgumentParser().parse_args()
    logging.basicConfig(level=logging.DEBUG)
    if args.nifti_file:
        niimg = nib.load(args.nifti_file)
        try:
            slice_onsets = niimg.header.get_slice_times() #change to support multiband
        except HeaderDataError:  # if data is slice time corrected, may not be in header
            print('assuming slice-timing-corrected data, using single slice')
            slice_onsets = [0] * niimg.shape[2]
        phys = NIMSPhysio(
            args.physio_file,
            tr=niimg.header.get_zooms()[3],
            nframes=niimg.shape[3],
            slice_onsets=slice_onsets,
            slice_window=float(args.slice_window)
        )
    else:
        log.warning('regressors will not be valid!')
        phys = NIMSPhysio(args.physio_file)
    if args.preprocess:
        np.savetxt(args.outbase + '_resp.txt', phys.resp_wave)
        np.savetxt(args.outbase + '_pulse.txt', phys.card_trig)
        np.savetxt(args.outbase + '_slice_onsets.txt', phys.slice_onsets)
    print('saving regressors out to %s_reg.tst' % args.outbase)
    phys.write_regressors(args.outbase + '_reg.txt')
    if args.nifti_file:
       d_corrected, PCT_VAR_REDUCED = phys.denoise_image(niimg.get_fdata(), phys.regressors)
       np.save(args.outbase+'_pct_var_reduced.npy', PCT_VAR_REDUCED)
       nib.save(nib.Nifti1Image(d_corrected, niimg.affine, niimg.header), args.outbase+'_prepoc-physio_bold.nii.gz')
