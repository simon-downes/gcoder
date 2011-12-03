
from gi.repository import GObject, Gedit, Gdk, Gtk

import document

class ViewHelper(GObject.Object, Gedit.ViewActivatable):
   __gtype_name__ = "gCoderViewHelper"

   view = GObject.property(type=Gedit.View)

   handlers = {}
   
   def __init__( self ):
      GObject.Object.__init__(self)

   def do_activate( self ):

      print 'Attaching gCoder to', self.view
      
      self.handlers['keypress'] = self.view.connect('key-press-event', self.on_key_press)
      self.handlers['copy']     = self.view.connect('copy-clipboard', self.copy_selection)
      self.handlers['cut']      = self.view.connect('cut-clipboard', self.cut_selection)

   def do_deactivate( self ):
      
      print 'Detatching gCoder from', self.view
      
      for signal, handler_id in self.handlers.iteritems():
         self.view.disconnect(handler_id)
      
   def copy_selection( self, view, data=None ):
      
      buf = view.get_buffer()
      
      if buf.get_has_selection():
         view.copy_clipboard()
      else:
	      # get start of current line and next line, select range and copy
	      start = buf.get_iter_at_mark(buf.get_insert())
	      start.set_line_offset(0)
	      end = start.copy()
	      end.forward_line()
	      buf.select_range(start, end)
	      view.copy_clipboard()
	      buf.place_cursor(start)
	  
      return True
      
   def cut_selection( self, view, data=None ):
      
      buf = view.get_buffer()
      buf.begin_user_action()
      
      if buf.get_has_selection():
         view.cut_clipboard()
      else:
	      # get start of current line and next line, select range and copy
	      start = buf.get_iter_at_mark(buf.get_insert())
	      start.set_line_offset(0)
	      end = start.copy()
	      end.forward_line()
	      buf.select_range(start, end)
	      view.cut_clipboard()
	   
      buf.end_user_action()
      return True
      
   def on_key_press( self, view, event, data=None ):
      
      # didn't do nuffink guv
      handled = False;
      
      # get a nice unicode character
      char = unichr(Gdk.keyval_to_unicode(event.keyval))
      
      # if we got a null char use None instead
      if char == '\0':
         char = None
      
      # ignore modifiers except ctrl, alt and shift
      state = event.state & Gtk.accelerator_get_default_mod_mask()
      
      # which modifier combo did we have
      is_alt        = state == Gdk.ModifierType.MOD1_MASK
      is_ctrl       = state == Gdk.ModifierType.CONTROL_MASK
      is_ctrl_shift = state == Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK
      
      #print gtk.gdk.keyval_name(event.keyval)
      
      buf = view.get_buffer()
      
      if is_ctrl:
         
         # ctrl + left - move cursor left one word
         if event.keyval == Gdk.KEY_Left:
            document.backward_word(buf, document.WORD_MOVE)
            self.view.scroll_mark_onscreen(buf.get_insert())
            handled = True
         
         # ctrl + right - move cursor right one word
         elif event.keyval == Gdk.KEY_Right:
            document.forward_word(buf, document.WORD_MOVE)
            self.view.scroll_mark_onscreen(buf.get_insert())
            handled = True
         
         # ctrl + backspace - delete to start/end of word
         elif event.keyval == Gdk.KEY_BackSpace:
            document.backward_word(buf, document.WORD_DELETE)
            self.view.scroll_mark_onscreen(buf.get_insert())
            handled = True
         
         # ctrl + delete - delete to start/end of word
         elif event.keyval == Gdk.KEY_Delete:
            document.forward_word(buf, document.WORD_DELETE)
            handled = True
         
      #   # ctrl + c - copy current line to clipboard if no selection
      #   elif event.keyval = Gdk.KEY_c:
      #      if not buf.get_has_selection():
      #         document.copy_line(buf, self.view.get_clipboard(gtk.gdk.SELECTION_CLIPBOARD), key == Gdk.KEY_x)
      #         handled = True
      #   
      #   # ctrl + x - cut current line to clipboard if no selection
      #   elif event.keyval = Gdk.KEY_x:
      #      if not buf.get_has_selection():
      #         document.copy_line(buf, self.view.get_clipboard(gtk.gdk.SELECTION_CLIPBOARD), key == Gdk.KEY_x)
      #         handled = True
      #   
      #   view.cut_clipboard()
      #   view.copy_clipboard() 
         
      elif is_ctrl_shift:
         
         # ctrl + shift + left - move cursor left one word
         if event.keyval == Gdk.KEY_Left:
            document.backward_word(buf, document.WORD_SELECT)
            handled = True
         
         # ctrl + shift + right - move cursor right one word
         elif event.keyval == Gdk.KEY_Right:
            document.forward_word(buf, document.WORD_SELECT)
            handled = True
         
         # ctrl + shift + A - select line
         elif event.keyval == Gdk.KEY_A:
            handled = document.select_line(view.get_buffer())
         
      elif is_alt:
         pass
      
      return handled
      
