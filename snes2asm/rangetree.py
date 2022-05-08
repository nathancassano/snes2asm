# -*- coding: utf-8 -*-

from copy import copy

class RangeTree():
	def __init__(self):
		self.root = None

	def find(self, index):
		node = self.root

		while node:
			if node.val == None:
				if node.left and node.left.contains(index):
					node = node.left
				elif node.right and node.right.contains(index):
					node = node.right
				else:
					return None
			elif node.contains(index):
				return node.val
			else:
				return None

	def items(self):
		items = []
		path = []
		stack = [self.root]
		while len(stack) != 0:

			node = stack.pop()
			if node not in path:
				path.append(node)

			if node.val:
				path.append(node)
				items.append(node.val)
			else:
				if node.right:
					stack.append(node.right)
				if node.left:
					stack.append(node.left)

		return items

	def intersects(self, start, end):
		node = self.root

		while node:
			if node.val == None:
				if node.left and node.left.intersects(start, end):
					node = node.left
				elif node.right and node.right.intersects(start, end):
					node = node.right
				else:
					return None
			elif node.intersects(start, end):
				return node.val
			else:
				return None

	def add(self, start, end, value):	
		new_node = RangeNode(start, end, value)

		if self.root == None:
			self.root = new_node
			return

		if self.root.intersects(new_node.start, new_node.end):
			self._add_inner(self.root, new_node)
		else:
			if start < self.root.start:
				self._split_node(self.root, start, self.root.end, new_node, True)
			else:
				self._split_node(self.root, self.root.start, end, new_node, False )

	def _add_inner(self, node, new_node):
		if node.val:
			raise ValueError("Range conflict")
			
		if node.left.intersects(new_node.start, new_node.end):
			self._add_inner(node.left, new_node)
		elif node.right.intersects(new_node.start, new_node.end):
			self._add_inner(node.right, new_node)
		else:
			left = node.left if node.left.size() <= node.right.size() else node.right
			if left:
				self._split_node(node.left, node.start, new_node.end, new_node, False)
			else:
				self._split_node(node.right, new_node.start, node.end, new_node, True)

	def _split_node(self, node, range_start, range_end, new_node, left):
		tmp_node = copy(node)
		node.val = None
		node.start = range_start
		node.end = range_end
		if left:
			node.left = new_node
			node.right = tmp_node
		else:
			node.left = tmp_node
			node.right = new_node

	def __str__(self):
		return str(self.root)

class RangeNode():
	def __init__(self, start, end, val=None):
		if end < start:
			raise ValueError("Invalid range %d-%d" % (start, end))
		self.start = start
		self.end = end;
		self.left = None
		self.right = None
		self.val = val

	def contains(self, index):
		return self.start <= index and index < self.end

	def intersects(self, start, end):
		return self.contains(start) or self.contains(end)

	def size(self):
		c = 1
		if self.left:
			c = c + self.left.size()
		if self.right:
			c = c + self.right.size()
		return c

	def __str__(self):
		s = "%s %d-%d [%d]\n" % (str(self.val), self.start, self.end, self.size()) if self.val else "R %d-%d [%d]\n" % (self.start, self.end, self.size())

		if self.left:
			s = s + "->" + str(self.left)
		if self.right:
			s = s + "->" + str(self.right)
		return s
