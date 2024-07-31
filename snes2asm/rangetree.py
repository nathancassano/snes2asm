# -*- coding: utf-8 -*-

"""
RangeTree is a tree structure for accessing data assigned to sequential
numerical ranges which are in non-overlapping.

tree = RangeTree()
tree.add(0, 100, "A")
tree.add(300,310, 42)

tree.find(50)
tree.intersects(200, 305)

"""

from copy import copy

class RangeTree():
	def __init__(self):
		self.root = None

	def find(self, index):
		"""
		Returns data value which index falls inside range entry
		"""
		node = self.root

		while node:
			if node.is_parent():
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
		"""
		Returns list of all data values in sequence
		"""
		items = []
		path = []
		stack = [self.root]
		while len(stack) != 0:
			node = stack.pop()
			if node not in path:
				path.append(node)

			if node.is_parent():
				if node.right:
					stack.append(node.right)
				if node.left:
					stack.append(node.left)
			else:
				path.append(node)
				items.append(node.val)
	
		return items

	def intersects(self, start, end):
		"""
		Returns left most data value that intersects with first range entry
		"""
		node = self.root

		while node:
			if node.is_parent():
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
		"""
		Add data entry assigned to numeric range
		"""
		new_node = _RangeNode(start, end, value)

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
		# Find tree node to insert new node into

		if not node.is_parent():
			raise ValueError("Range conflict")
			
		if node.left.intersects(new_node.start, new_node.end):
			self._add_inner(node.left, new_node)
		elif node.right.intersects(new_node.start, new_node.end):
			self._add_inner(node.right, new_node)
		else:
			left = node.left.size() <= node.right.size()
			if left:
				self._split_node(node.left, node.start, new_node.end, new_node, False)
			else:
				self._split_node(node.right, new_node.start, node.end, new_node, True)

	def _split_node(self, node, range_start, range_end, new_node, left):
		# Create parent node to contain original node and new node
		tmp_node = copy(node)
		node.val = None # Mark as parent
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

class _RangeNode():
	def __init__(self, start, end, val):
		if end < start:
			raise ValueError("Invalid range %d-%d" % (start, end))
		self.start = start
		self.end = end
		self.left = None
		self.right = None
		self.val = val

	def contains(self, index):
		return self.start <= index and index < self.end

	def intersects(self, start, end):
		return min(self.end, end) - max(self.start, start) > 0

	def width(self):
		return self.end - self.start

	def size(self):
		c = 1
		if self.left:
			c = c + self.left.size()
		if self.right:
			c = c + self.right.size()
		return c

	def is_parent(self):
		return self.val == None

	def __str__(self):
		if self.is_parent():
			s = "{%x-%x (%x)\n" % (self.start, self.end, self.size())
			s = s + "[%s]\n[%s] }" % (str(self.left), str(self.right))
		else:
			s = "N %x-%x => %s" % (self.start, self.end, str(self.val))
		return s
