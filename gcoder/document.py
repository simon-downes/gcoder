# -*- coding: utf-8 -*-
#
# gCoder plugin for gedit
#
# See README for info or go to http://code.google.com/p/gextras/
#
# Copyright (c) 2010-2011, Simon Downes <simon@simondownes.co.uk>
#
# Licensed under the MIT License;
# A copy of the license is included in the LICENSE file accompanying this
# distribution or online at http://www.opensource.org/licenses/mit-license.php

# Functions to convert:
# comment_selection
# uncomment_selection
# highlight_line
#

from gi.repository import Gtk

BREAK_CHARS = '_='

WORD_MOVE   = 0
WORD_DELETE = 1
WORD_SELECT = 2

CASE_UPPER      = 1
CASE_LOWER      = 2
CASE_CAPITALISE = 3
CASE_SENTENCE   = 4
CASE_INVERT     = 5

def select_line( buf ):
	start = buf.get_iter_at_mark(buf.get_insert())
	start.set_line_offset(0)
	end = start.copy()
	end.forward_line()
	buf.select_range(start, end)
	return True

def backward_word( buf, mode=WORD_MOVE ):
	
	pos = buf.get_iter_at_mark(buf.get_insert())
	
	if pos.starts_line():
		pos.backward_char()
	
	# if we're at the start of the word then check if there's anything apart from word chars
	# and spaces (all whitespace?) between here and the start of the previous word
	# if not then go back to the start of the previous word
	# otherwise go back to the end of the previous word
	elif starts_word(pos):
		search = pos.copy()
		search.backward_char()
		found = False
		while not search.is_start() and not starts_word(search):
			search.backward_char()
			if not inside_word(search) and search.get_char() != ' ':
				found = True
				break
		
		if found:
			while not pos.is_start() and not pos.starts_line() and not ends_word(pos):
				pos.backward_char()
		else:
			pos.backward_char()
			while not pos.is_start() and not pos.starts_line() and not starts_word(pos):
				pos.backward_char()
	
	# if we're inside a word or at the end then go back to the start
	elif inside_word(pos) or ends_word(pos):
		pos.backward_char()
		while not pos.is_start() and not starts_word(pos):
			pos.backward_char()
	
	# we're not in a word or at the start or end of one
	# so go back to the end of the previous word
	else:
		pos.backward_char()
		while not pos.is_start() and not pos.starts_line() and not ends_word(pos):
			pos.backward_char()
	
	if mode == WORD_DELETE :
		start = buf.get_iter_at_mark(buf.get_insert())
		buf.begin_user_action()
		buf.delete(start, pos)
		buf.end_user_action()
	elif mode == WORD_SELECT:
		start = buf.get_iter_at_mark(buf.get_selection_bound())
		buf.select_range(pos, start)
	else:
		buf.place_cursor(pos)

def forward_word( buf, mode=WORD_MOVE ):
	
	pos = buf.get_iter_at_mark(buf.get_insert())
	
	if pos.ends_line():
		pos.forward_char()
	
	# if we're inside a word or at the start then go forward to the end
	elif inside_word(pos) or starts_word(pos):
		
		search = pos.copy()
		search.forward_char()
		found = False
		while not search.is_end() and not starts_word(search):
			search.forward_char()
			if not inside_word(search) and search.get_char() != ' ':
				found = True
				break
		
		if found:
			while not pos.is_end() and not pos.ends_line() and not ends_word(pos):
				pos.forward_char()
		else:
			pos.forward_char()
			while not pos.is_end() and not pos.ends_line() and not starts_word(pos):
				pos.forward_char()
	
	# if at the start of the line and on whitespace go forward to first non-whitespace char
	elif pos.starts_line() and pos.get_char().isspace():
		while not pos.is_end() and pos.get_char().isspace():
			pos.forward_char()
	
	else:
		pos.forward_char()
		while not pos.is_end() and not pos.ends_line() and not starts_word(pos):
			pos.forward_char()
	
	if mode == WORD_DELETE :
		start = buf.get_iter_at_mark(buf.get_insert())
		buf.begin_user_action()
		buf.delete(start, pos)
		buf.end_user_action()
	elif mode == WORD_SELECT:
		start = buf.get_iter_at_mark(buf.get_selection_bound())
		buf.select_range(pos, start)
	else:
		buf.place_cursor(pos)

def starts_word( pos ):
	
	# if we're inside a word then work backwards to the end of the previous word
	# and check for word characters, if we find any, we're not at the start of the word yet
	if inside_word(pos):
		at_start = True   
		search = pos.copy()
		while not search.is_start() and not ends_word(search):
			search.backward_char()
			if inside_word(search):
				at_start = False
				break;
	
	# if we're not inside at word then we're at the start if the iter says so
	else:
		at_start = pos.starts_word()
	
	return at_start

def ends_word( pos ):
	
	# not a the end if we're still inside a word, duh
	if inside_word(pos):
		at_end = False
	# we are at the end if the iter says so or the previous character was in BREAK_CAHRS
	else:
		pos.backward_char()
		previous_char = pos.get_char()
		pos.forward_char()
		at_end = pos.ends_word() or previous_char in BREAK_CHARS
	
	return at_end

# we're in a word if the iter says so or the next character is in BREAK_CAHRS
def inside_word( pos ):
	return pos.inside_word() or pos.get_char() in BREAK_CHARS

def copy_line( buf, clipboard, cut=False ):
	
	# get start of current line and next line
	start = buf.get_iter_at_mark(buf.get_insert())
	start.set_line_offset(0)
	end = start.copy()
	end.forward_line()
	
	# select the line and cut/copy it to the clipboard
	buf.begin_user_action()
	buf.select_range(start, end)
	if cut:
		buf.cut_clipboard(clipboard, True)
	else:
		buf.copy_clipboard(clipboard)
		buf.place_cursor(start)
	buf.end_user_action()
	
def change_case( buf, new_case ):
	
	selection = buf.get_selection_bounds()
	
	if selection:
		
		# extract selection
		start, end = selection
		
		# create marks so we can reselect the text after we've changed the case
		(mark_start, mark_end) = mark_range(buf, start, end)
		#mark_start = buf.create_mark(None, start, True)
		#mark_end   = buf.create_mark(None, end, False)
		
		# get the selection, modify it and update the document
		sel_text = start.get_text(end)
		
		if new_case == CASE_UPPER:
			sel_text = sel_text.upper()
		elif new_case == CASE_LOWER:
			sel_text = sel_text.lower()
		elif new_case == CASE_CAPITALISE:
			sel_text = sel_text.title()
		elif new_case == CASE_SENTENCE:
			sel_text = sel_text.capitalize()       # TODO: custom function that capitalises multiple sentences
		elif new_case == CASE_INVERT:
			sel_text = sel_text.swapcase()
		else:
			sel_text = None
		
		# update the document and reselect the text we changed
		if sel_text:
			buf.begin_user_action()
			buf.delete(start, end)
			buf.insert(start, sel_text)
			buf.select_range(buf.get_iter_at_mark(mark_start), buf.get_iter_at_mark(mark_end))
			buf.end_user_action()
		
		# cleanup
		buf.delete_mark(mark_start)
		buf.delete_mark(mark_end)

def comment_selection( buf, comment_tag, tab_char=' ' ):
	
	selection = buf.get_selection_bounds()
	
	# expand selection to start and end of lines
	if selection:
		start, end= selection
		start.set_line_offset(0)
		if not end.ends_line():
			end.forward_to_line_end()
	# if no selection use current line
	else:
		start = buf.get_iter_at_mark(buf.get_insert())
		start.set_line_offset(0)
		end = start.copy()
		if not end.ends_line():
			end.forward_to_line_end()
	
	# create marks so we can reselect the text after we've commented it
	(mark_start, mark_end) = mark_range(buf, start, end)
	#mark_start = buf.create_mark(None, start, True)
	#mark_end   = buf.create_mark(None, end, False)
	
	line_offset = start.get_line()
	line_count  = end.get_line() - line_offset + 1	
	
	# locate the minimum offset to a non-whitespace character
	# this will be the line offset at which the comment tag is inserted
	offsets = [];
	pos = start.copy()
	for i in range(0, line_count):
		while pos.get_char().isspace():
			pos.forward_char()
		offsets.append(pos.get_line_offset())
		pos.forward_line()
	char_offset = min(offsets)
	
	buf.begin_user_action()
	
	for i in range(0, line_count):
		
		pos = buf.get_iter_at_line(line_offset + i)
		
		# if we're at the end of the line it's empty so pad to char_offset with tab_char
		if pos.ends_line():
			buf.insert(pos, tab_char * (char_offset) + comment_tag)
		
		# otherwise go to the end of the line;
		# if we're under char_offset pad with tab_char until we reach it,
		# otherwise rewind to char_offset
		else:
			pos.forward_to_line_end()
			if pos.get_line_offset() < char_offset:
				buf.insert(pos, tab_char * (char_offset - pos.get_line_offset()) + comment_tag)
			else:
				pos.set_line_offset(char_offset)
				buf.insert(pos, comment_tag)
			
	buf.end_user_action()
	
	buf.select_range(buf.get_iter_at_mark(mark_start), buf.get_iter_at_mark(mark_end))
	
	# clean up
	buf.delete_mark(mark_start)
	buf.delete_mark(mark_end)
	
def uncomment_selection( buf, comment_tag ):
	
	selection = buf.get_selection_bounds()
	
	if selection:
		start, end = selection
		start.set_line_offset(0)
		if not end.ends_line():
			end.forward_to_line_end()
	# if no selection use current line
	else:
		start = buf.get_iter_at_mark(buf.get_insert())
		start.set_line_offset(0)
		end = start.copy()
		if not end.ends_line():
			end.forward_to_line_end()
	
	# create marks so we can reselect the text after we've changed the case
	(mark_start, mark_end) = mark_range(buf, start, end)
	#mark_start = buf.create_mark(None, start, True)
	#mark_end   = buf.create_mark(None, end, False)
	
	line_offset = start.get_line()
	line_count  = end.get_line() - line_offset + 1
	
	buf.begin_user_action()
	
	for i in range(0, line_count):
		
		pos = buf.get_iter_at_line(line_offset + i)
		
		while pos.get_char().isspace():
			pos.forward_char()
		
		end = pos.copy()
		end.forward_chars( len(comment_tag) )
		
		if pos.get_slice(end) == comment_tag:
			buf.delete(pos, end)
		
	buf.end_user_action()
	
	buf.select_range(buf.get_iter_at_mark(mark_start), buf.get_iter_at_mark(mark_end))
	
	# clean up
	buf.delete_mark(mark_start)
	buf.delete_mark(mark_end)

def highlight_line( buf, line, highlight=True ):
	
	tag_table = buf.get_tag_table()
	tag = tag_table.lookup("gcoder.bookmark")
	
	if tag is None:
		tag = buf.create_tag("gcoder.bookmark", paragraph_background_gdk = gtk.gdk.color_parse('#ffffcc'))
	
	start = buf.get_iter_at_line(line)
	end = start.copy()
	end.forward_to_line_end()
	
	if highlight:
		buf.apply_tag(tag, start, end)
	else:
		buf.remove_tag(tag, start, end)

# return a tuple of marks at the specified text_iters
def mark_range(buf, start, end):
   return (buf.create_mark(None, start, True), buf.create_mark(None, end, False))
		
