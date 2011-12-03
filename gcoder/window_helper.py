
import os

from gi.repository import GObject, Gedit, Gdk, Gtk

import document

ui_str = """<ui>
   <menubar name="MenuBar">
      <menu name="EditMenu" action="Edit">
         <placeholder name="EditOps_3">
            <menuitem name="gCoderSelectLine" action="gCoderSelectLine"/>
            <separator/>
            <menuitem name="gCoderUppercase" action="gCoderUppercase"/>
            <menuitem name="gCoderLowercase" action="gCoderLowercase"/>
            <menu name="gCoderOtherCase" action="gCoderOtherCase">
               <menuitem name="gCoderCapitalise" action="gCoderCapitalise"/>
               <menuitem name="gCoderSentenceCase" action="gCoderSentenceCase"/>
               <menuitem name="gCoderInvertCase" action="gCoderInvertCase"/>
            </menu>
            <separator/>
            <menuitem name="gCoderComment" action="gCoderComment"/>
            <menuitem name="gCoderUncomment" action="gCoderUncomment"/>
            <separator/>
            <menuitem name="gCoderToggleBookmark" action="gCoderToggleBookmark"/>
            <menuitem name="gCoderPreviousBookmark" action="gCoderPreviousBookmark"/>
            <menuitem name="gCoderNextBookmark" action="gCoderNextBookmark"/>
            <separator/>
         </placeholder>
      </menu>
      <menu name="ViewMenu" action="View">
         <placeholder name="gExtraViewOps">
         </placeholder>
      </menu>
      <menu name="DocumentsMenu" action="Documents">
         <placeholder name="DocumentsOps_1">
            <separator/>
            <menuitem name="gCoderPreviousDocument" action="gCoderPreviousDocument"/>
            <menuitem name="gCoderNextDocument" action="gCoderNextDocument"/>
         </placeholder>
      </menu>
   </menubar>
</ui>
"""

class WindowHelper(GObject.Object, Gedit.WindowActivatable):
   __gtype_name__ = "gCoderWindowHelper"

   window = GObject.property(type=Gedit.Window)
   
   action_group = None;
   ui_id = None;
   
   handlers = {}
   
   def __init__( self ):
      GObject.Object.__init__(self)
      self.path = os.path.dirname( __file__ )
      
   def do_activate( self ):
      
      print 'Attaching gCoder to', self.window
      
      self.add_ui()
      
      # TODO: will be used for bookmarks - display bookmarks for current view on tab change
      #self.handlers['tab-added'] = self.window.connect('tab-added', self.on_tab_added)
      #self.handlers['tab-removed'] = self.window.connect('tab-added', self.on_tab_removed)
      #self.handlers['active-tab-changed'] = self.window.connect('tab-added', self.on_tab_changed)
      
      self.handlers['keypress'] = self.window.connect('key-press-event', self.on_key_press)
      
   def do_deactivate( self ):
      
      print 'Detatching gCoder from', self.window
      
      self.remove_ui()
      
      for signal, handler_id in self.handlers.iteritems():
         self.window.disconnect(handler_id)
      
   def do_update_state( self ):
      self.update_ui()
   
   def add_ui( self ):
      
      # Get the Gtk.UIManager
      manager = self.window.get_ui_manager()
      
      self.action_group = Gtk.ActionGroup("gCoderPluginActions")
      self.action_group.add_actions([
         
         # edit menu
         ("gCoderSelectLine", None, 'Select L_ine', '<Control><Shift>a', 'Select the current line', self.select_line),
         ("gCoderUppercase", None, 'Make _Uppercase', '<Control>u', 'Make current selection uppercase', self.change_case),
         ("gCoderLowercase", None, 'Make _Lowercase', '<Control>l', 'Make current selection lowercase', self.change_case),
         ("gCoderOtherCase", None, '_Other Case', None, 'Other case options', None),
            ("gCoderCapitalise", None, 'Capitalise', None, 'Capitalise first letters of words in selection', self.change_case),
            ("gCoderSentenceCase", None, 'Sentence Case', None, 'Capitalise first letters of first words of sentences in selection', self.change_case),
            ("gCoderInvertCase", None, 'Invert Case', None, 'Invert case of selection', self.change_case),
         ("gCoderComment", None, 'Co_mment', '<Control>m', 'Comment the current selection', self.comment_selection),
         ("gCoderUncomment", None, 'U_n-comment', '<Control><Shift>m', 'Un-comment the current selection', self.comment_selection),
         ("gCoderToggleBookmark", None, 'Toggle _Bookmark', '<Control>e', 'Toggle a bookmark on the current line', self.empty_action),
         ("gCoderPreviousBookmark", None, 'Previous Bookmark', '<Control>comma', 'Scroll to the previous bookmark', self.empty_action),
         ("gCoderNextBookmark", None, 'Next Bookmark', '<Control>period', 'Scroll to the next bookmark', self.empty_action),
         
         # documents menu
         ("gCoderPreviousDocument", None, '_Previous Document', '<Control><Shift>Tab', 'Select previous document', self.tab_switch),
         ("gCoderNextDocument", None, '_Next Document', '<Control>Tab', 'Select next document', self.tab_switch),
         
         # shortcuts only, no menu items
         ("gCoderScrollUp", None, 'Scroll Up', '<Control>Up', 'Scroll up one line', self.scroll_line),
         ("gCoderScrollDown", None, 'Scroll Down', '<Control>Down', 'Scroll down one line', self.scroll_line),
         
         #("", None, '', None, '', self._empty_action)
         #(Name, None, Label, Accelerator, Tooltip, Callback)
         
      ])
      
      # insert our cool stuff
      manager.insert_action_group(self.action_group, -1)
      self.ui_id = manager.add_ui_from_string(ui_str)
      
      # hide existing next/previous document items
      for k in ['DocumentsMenu/DocumentsNextDocument', 'DocumentsMenu/DocumentsPreviousDocument']:
         item = manager.get_widget('/MenuBar/' + k)
         if isinstance(item, Gtk.Widget):
            item.hide()
      
      # display pretty icons for some menu items
      icons = {
         'EditMenu': {
            'gCoderToggleBookmark'  : 'bookmark-new.svg',
            'gCoderPreviousBookmark': 'bullet_left.png',
            'gCoderNextBookmark'    : 'bullet_right.png'
         },
         'DocumentsMenu': {
            'gCoderPreviousDocument': 'page_back.png',
            'gCoderNextDocument'    : 'page_forward.png'
         }
      }
      for k in icons.keys():
         for item in manager.get_widget('/MenuBar/' + k).get_submenu().get_children():
            if item.get_name() in icons[k]:
               icon = Gtk.Image()
               icon.set_from_file(self.path + '/icons/' + icons[k][item.get_name()])
               item.set_image(icon)
      
      manager.ensure_update()
      
      #for action_group in manager.get_action_groups():
      #   print action_group.get_name()
      #   for action in action_group.list_actions():
      #      print ' |-', action.get_name()
      
      #print manager.get_ui()
      
   def remove_ui( self ):
      
      manager = self.window.get_ui_manager()
      
      # restore original next/previous document items
      item = manager.get_widget('/MenuBar/DocumentsMenu/DocumentsNextDocument')
      if isinstance(item, Gtk.Widget):
         item.show()
      
      item = manager.get_widget('/MenuBar/DocumentsMenu/DocumentsPreviousDocument')
      if isinstance(item, Gtk.Widget):
         item.show()
      
      # remove the junk we inserted and make sure the UI updates
      manager.remove_ui(self.ui_id)
      manager.remove_action_group(self.action_group)
      manager.ensure_update()
      
   def update_ui( self ):
      self.action_group.set_sensitive( self.window.get_active_document() != None )
   
   def empty_action( self, action ):
      print action.get_name()
      return True
   
   def select_line( self, action ):
      doc = self.window.get_active_document()
      if doc:
         document.select_line(doc)
      return True
   
   def scroll_line( self, action ):
      
      view = self.window.get_active_view()
      doc  = self.window.get_active_document()
      
      if view and doc:
         
         # get the position of the cursor on the current line
         pos = doc.get_iter_at_mark(doc.get_insert())
         col = pos.get_line_offset()
         
         # get the character position at the top of the visible area
         viewport = view.get_visible_rect()
         
         if action.get_name() == 'gCoderScrollUp':
            pos = view.get_iter_at_location(viewport.x, viewport.y)
            pos.backward_line()
         else:
            # don't need to call forward_line() as y + height already gives us the next line just below the current viewport
            pos = view.get_iter_at_location(viewport.x, viewport.y + viewport.height)
         
         view.scroll_to_iter(pos, 0.0, False, 0, 0)
         
         # make sure the cursor is on the screen, otherwise it can scroll off the bottom
         view.place_cursor_onscreen()
         
         # get the new cursor position and move it to the previous column position
         # or the end of the line if line is too short
         pos = doc.get_iter_at_mark(doc.get_insert())
         max_col = pos.get_chars_in_line() - 1
         if col < max_col:
            pos.set_line_offset(col)
         else:
            pos.set_line_offset(max_col)
         
         doc.place_cursor(pos)
      
      return True
   
   def change_case( self, action ):
      doc = self.window.get_active_document()
      if doc:
         action_name = action.get_name()
         if action_name == 'gCoderUppercase':
            document.change_case(doc, document.CASE_UPPER)
         elif action_name == 'gCoderLowercase':
            document.change_case(doc, document.CASE_LOWER)
         elif action_name == 'gCoderCapitalise':
            document.change_case(doc, document.CASE_CAPITALISE)
         elif action_name == 'gCoderSentenceCase':
            document.change_case(doc, document.CASE_SENTENCE)
         elif action_name == 'gCoderInvertCase':
            document.change_case(doc, document.CASE_INVERT)
      return True
   
   def comment_selection( self, action ):
      
      doc  = self.window.get_active_document()
      view = self.window.get_active_view()
      
      if doc and view:
         
         lang = doc.get_language()
         if lang is None:
             return True
         
         comment_tag = lang.get_metadata('line-comment-start')
         if not comment_tag:
             return True
         
         if view.get_insert_spaces_instead_of_tabs():
            tab_char = ' '
         else:
            tab_char = "\t"
         
         if action.get_name() == 'gCoderComment':
            document.comment_selection(doc, comment_tag, tab_char)
         else:
            document.uncomment_selection(doc, comment_tag)
         
      return True
   
   def tab_switch( self, action ):
      
      active_tab = self.window.get_active_tab()
      all_tabs   = active_tab.get_parent().get_children()
      num_tabs   = len(all_tabs)
      
      i = 0
      for tab in all_tabs:
          i += 1
          if tab == active_tab:
              break
      
      if action.get_name() == 'gCoderPreviousDocument':
          i -= 2
      
      if i < 0:
          tab = all_tabs[num_tabs - 1]
      elif i >= num_tabs:
          tab = all_tabs[0]
      else:
          tab = all_tabs[i]
      
      self.window.set_active_tab(tab)
      
      return True
   
   def on_key_press( self, window, event, data=None ):
      
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
      
      if is_ctrl:
         
         # ctrl + tab - next document
         if event.keyval in [Gdk.KEY_Tab, Gdk.KEY_ISO_Left_Tab]:
            handled = self.tab_switch( self.action_group.get_action('gCoderNextDocument') )
         
         # ctrl + up - scroll one line
         elif event.keyval == Gdk.KEY_Up:
            handled = self.scroll_line( self.action_group.get_action('gCoderScrollUp') )
         
         # ctrl + down - scroll one line
         elif event.keyval == Gdk.KEY_Down:
            handled = self.scroll_line( self.action_group.get_action('gCoderScrollDown') )
         
      elif is_ctrl_shift:
         
         # ctrl + shift + tab - previous document
         if event.keyval in [Gdk.KEY_Tab, Gdk.KEY_ISO_Left_Tab]:
            handled = self.tab_switch( self.action_group.get_action('gCoderPreviousDocument') )
         
      elif is_alt:
         pass
      
      return handled
      
