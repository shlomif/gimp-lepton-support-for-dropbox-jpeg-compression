#!/usr/bin/env python3
#
# -------------------------------------------------------------------------------------
#
# Copyright (c) 2013, Jose F. Maldonado
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification,
# are permitted provided that the following conditions are met:
#
#    - Redistributions of source code must retain the above copyright
#    notice, this
#    list of conditions and the following disclaimer.
#    - Redistributions in binary form must reproduce the above
#    copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or
#    other materials provided with the distribution.
#    - Neither the name of the author nor the names of its contributors may
#    be used
#    to endorse or promote products derived from this software without specific
#    prior
#    written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# ================
#
# Also based on:
# https://gitlab.gnome.org/GNOME/gimp/-/blob/
# ffc7db84d1834a8720fcf2b6109b97c3a0e3adf7/
# /plug-ins/python/file-openraster.py
#
# (short URL: https://is.gd/M53O7I )
#
# ==================
#
# GIMP Plug-in for the OpenRaster file format
# http://create.freedesktop.org/wiki/OpenRaster

# Copyright (C) 2009 by Jon Nordby <jononor@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Based on MyPaint source code by Martin Renold
# http://gitorious.org/mypaint/mypaint/blobs/
# edd84bcc1e091d0d56aa6d26637aa8a925987b6a/lib/document.py
#
# ==================
#
# Based on https://github.com/jfmdev/PythonFuSamples
# Thanks!
#  -- Shlomi Fish

import os.path
import subprocess
import shutil
import sys
from tempfile import mkdtemp

import gi
gi.require_version('Gimp', '3.0')

from gi.repository import Gimp  # noqa: E402
from gi.repository import Gio  # noqa: E402
from gi.repository import GObject  # noqa: E402

FILE_TYPE = Gio.File.__gtype__


def load_lep(procedure, run_mode, fileobj, args, data):
    Gimp.progress_init("Opening '" + fileobj.peek_path() + "'...")

    try:
        tmpdirobj = mkdtemp()
        tmp_dirname = tmpdirobj
        jpeg_fn = os.path.join(tmp_dirname, "from_lep.jpeg")
        subprocess.check_call(["lepton", fileobj.peek_path(), jpeg_fn])

        args = Gimp.ValueArray.new(2)
        arg0 = GObject.Value(Gimp.RunMode, Gimp.RunMode.NONINTERACTIVE)
        args.insert(0, arg0)
        arg2 = GObject.Value(FILE_TYPE, Gio.File.new_for_path(jpeg_fn))
        args.insert(1, arg2)
        # jpeg_fn, fileobj.peek_path())
        fileImage = Gimp.get_pdb().run_procedure('file-jpeg-load', args)
        if(fileImage is None):
            Gimp.message("The image could not be opened since" +
                         "it is not an image file.")
        shutil.rmtree(tmp_dirname)
        return fileImage
    except Exception as err:
        Gimp.message("Unexpected error: " + str(err))
        raise err


"""
    "JFM",
    "Open source (BSD 3-clause license)",
    "2013",
    "Lepton",
    None,  # image type
    [
        (PF_STRING, "filename", "File to open", None),
        (PF_STRING, "raw-filename", "Name entered", None),
    ],
    [(PF_IMAGE, 'image', 'Output image'), ],
    file_load_lepton,
    on_query=register_load_handlers,
    menu="<Load>",
    )
"""


class FileLepton (Gimp.PlugIn):
    def do_query_procedures(self):
        self.set_translation_domain(
            "gimp30-python",
            Gio.file_new_for_path(Gimp.locale_directory()))

        return ['file-lepton-load']
        return ['file-lepton-load-thumb',
                'file-lepton-load',
                'file-lepton-save', ]

    def do_create_procedure(self, name):
        if name == 'file-lepton-save':
            def save_lep():
                return
            procedure = Gimp.SaveProcedure.new(self, name,
                                               Gimp.PDBProcType.PLUGIN,
                                               save_lep, None)
            procedure.set_image_types("*")
            procedure.set_documentation('save a Lepton (.lep) file',
                                        'save a Lepton (.lep) file',
                                        name)
            procedure.set_menu_label('Lepton')
            procedure.set_extensions("lep")
        elif name == 'file-lepton-load':
            procedure = Gimp.LoadProcedure.new(self, name,
                                               Gimp.PDBProcType.PLUGIN,
                                               load_lep, None)
            procedure.set_menu_label('Lepton')
            procedure.set_documentation('load a Lepton (.lep) file',
                                        'load a Lepton (.lep) file',
                                        name)
            procedure.set_mime_types("image/lepton")
            procedure.set_extensions("lep")
            procedure.set_thumbnail_loader('file-lepton-load-thumb')
        else:  # 'file-lepton-load-thumb'
            def thumbnail_lep():
                return
            procedure = Gimp.ThumbnailProcedure.new(self, name,
                                                    Gimp.PDBProcType.PLUGIN,
                                                    thumbnail_lep, None)
            procedure.set_documentation(
                'loads a thumbnail from a Lepton (.lep) file',
                'loads a thumbnail from a Lepton (.lep) file',
                name)
            pass
        procedure.set_attribution('Jon Nordby',  # author
                                  'Jon Nordby',  # copyright
                                  '2009')  # year
        return procedure


Gimp.main(FileLepton.__gtype__, sys.argv)
