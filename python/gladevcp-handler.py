#!/usr/bin/env python

import os,sys
from gladevcp.persistence import IniFile,widget_defaults,set_debug,select_widgets
import hal
import hal_glib
import gtk
import glib
import linuxcnc

class HandlerClass:

    def on_tool_change_set_xyz_clicked(self,widget,data=None):
       s = linuxcnc.stat() # create a connection to the status channel
       s.poll() # get current values
       self.builder.get_object('tool_change_pos_x').set_value(s.actual_position[0])
       self.builder.get_object('tool_change_pos_y').set_value(s.actual_position[1])
       self.builder.get_object('tool_change_pos_z').set_value(s.actual_position[2])

    def on_tool_probe_set_xyz_clicked(self,widget,data=None):
       s = linuxcnc.stat() # create a connection to the status channel
       s.poll() # get current values
       self.builder.get_object('tool_probe_pos_x').set_value(s.actual_position[0])
       self.builder.get_object('tool_probe_pos_y').set_value(s.actual_position[1])
       self.builder.get_object('tool_probe_pos_z').set_value(s.actual_position[2])


    def on_probe_touchoff_pressed(self,widget,data=None):
        print "Probe touch off pressed"

    def on_led_change(self,hal_led,data=None):
        '''
        the gladevcp.change led had a transition
        '''
        if hal_led.hal_pin.get():
            if self.halcomp["number"] > 0.0:
                self.change_text.set_label("Insert tool number %d" % (int(self.halcomp["number"])))
            else:
                self.change_text.set_label("Remove tool")
        else:
            self.change_text.set_label("")

    def on_unix_signal(self,signum,stack_frame):
        print "on_unix_signal(): signal %d received, saving state" % (signum)
        self.ini.save_state(self)
        gtk.main_quit()
        self.halcomp.exit()

    def on_destroy(self,obj,data=None):
        '''
        gladevcp_demo.ui has a destroy callback set in the window1 Gobject
        note the widget tree is not safely accessible here any more
        '''
        print "on_destroy() - saving state)"
        self.ini.save_state(self)

    def __init__(self, halcomp,builder,useropts):
        self.halcomp = halcomp
        self.builder = builder
        
        (directory,filename) = os.path.split(__file__)
        (basename,extension) = os.path.splitext(filename)
        self.ini_filename = os.path.join(directory,basename + '.ini')

        self.defaults = {  # these will be saved/restored as method attributes
                            IniFile.vars: { 'probe_feed' : 1, 'probe_max': 2, 'plate_thickness': 3, 'z_retract': 4},

                            # we're interested restoring state to output HAL widgets only
                            # NB: this does NOT restore state pf plain gtk objects - set hal_only to False to do this
                            IniFile.widgets: widget_defaults(select_widgets(self.builder.get_objects(), hal_only=False,output_only = True)),
                       }

        self.ini = IniFile(self.ini_filename,self.defaults, self.builder)
        self.ini.restore_state(self)
        ''' self._hal_setup(halcomp,builder) '''

        self.change_text = builder.get_object("change-text")
        self.halcomp.newpin("number", hal.HAL_FLOAT, hal.HAL_IN)

def get_handlers(halcomp,builder,useropts):
    return [HandlerClass(halcomp,builder,useropts)]
