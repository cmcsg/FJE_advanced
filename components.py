# components.py

class Component:
    def __init__(self, name, icon):
        self.name = name
        self.icon = icon

    def accept(self, visitor):
        raise NotImplementedError("This method should be overridden by subclasses")

    def draw(self, indent="", is_last=True):
        raise NotImplementedError("This method should be overridden by subclasses")

    def create_iterator(self):
        return NoneIterator()


class NoneIterator:
    def has_next(self):
        return False

    def next(self):
        return None


class CompositeIterator:
    def __init__(self, children):
        self.stack = []
        if children:
            self.stack.extend(reversed(children))

    def has_next(self):
        return len(self.stack) > 0

    def next(self):
        if self.has_next():
            component = self.stack.pop()
            if hasattr(component, 'children'):
                self.stack.extend(reversed(component.children))
            return component
        return None


class Container(Component):
    def __init__(self, name, icon):
        super().__init__(name, icon)
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def draw(self, indent="", is_last=False):
        pass  # Base Container does not implement drawing

    def create_iterator(self):
        return CompositeIterator(self.children)

    def accept(self, visitor):
        visitor.visit_container(self)


class TreeContainer(Container):
    def draw(self, indent="r", is_last=True):  # 这里last指的是同一层的最后一位
        # Draw current container node
        if indent == "r":
            new_indent = ""
        else:
            prefix = f"{indent}{'└─' if is_last else '├─'}"
            print(f"{prefix}{self.icon} {self.name}")
            # Preparing the new indent for child nodes
            new_indent = indent + ("    " if is_last else "│   ")

        # Draw all child nodes
        for i, child in enumerate(self.children):
            child.draw(new_indent, i == len(self.children) - 1)


class RectangleContainer(Container):
    def draw(self, indent="r", is_last=True, max_length=0):  # 注意，这里的last指整个图的最后一行
        if indent == "r":
            is_last = len(self.children) == 1  # 由于提前处理第一行，先判断第一行在这一层中是不是最后一位
            max_length = self.max_length()
            # Calculate the length of the line for the box
            line_length = max_length - len(f"{self.children[0].icon} {self.children[0].name}")
            prefix = f"{'┌─'}"
            postfix = "─"*line_length+f"{'─┐'}"
            print(f"{prefix}{self.children[0].icon} {self.children[0].name}{postfix}")
            new_indent = "│   "
            for i, child in enumerate(self.children[0].children):
                child.draw(new_indent, i == len(self.children[0].children) - 1 and is_last, max_length)
            self.children.pop(0)
            is_last = True  # 这里表现的是根结点
        else:
            # Calculate the length of the line for the box
            line_length = max_length - len(indent + f"{self.icon} {self.name}")
            prefix = f"{indent}{'├─'}"
            postfix = "─"*line_length+f"{'─┤'}"
            print(f"{prefix}{self.icon} {self.name}{postfix}")
            new_indent = indent + "│   "

        # Draw all child nodes
        for i, child in enumerate(self.children):
            child.draw(new_indent, i == len(self.children) - 1 and is_last, max_length)

    def max_length(self, indent_length=0):
        # 找到可能到达的最后位置，以保证矩形在每行的最后一列一致
        current_length = indent_length + len(f"{self.icon} {self.name}")
        children_max_length = max((child.max_length(indent_length + 3) for child in self.children), default=0)
        return max(current_length, children_max_length)


class Leaf(Component):
    def __init__(self, name, icon):
        super().__init__(name, icon)

    def draw(self, indent="", is_last=True):
        pass  # Base Leaf does not implement drawing

    def accept(self, visitor):
        visitor.visit_leaf(self)


class TreeLeaf(Leaf):
    def draw(self, indent="", is_last=True):
        prefix = f"{indent}{'└─' if is_last else '├─'}"
        print(f"{prefix}{self.icon} {self.name}")


class RectangleLeaf(Leaf):
    def draw(self, indent="", is_last=True, max_length=0):
        line_length = max_length - len(indent+f"{self.icon} {self.name}")
        if is_last:
            indent = indent.replace("│   ", "└───", 1)  # 最后一行替换
            indent = indent.replace("│   ", "┴───")
            if len(indent) == 0:  # 判断在不在第一列
                prefix = f"{indent}{'└─'}"
            else:
                prefix = f"{indent}{'┴─'}"
        else:
            prefix = f"{indent}{'└─' if is_last and len(indent) == 0 else  '├─'}"
        postfix = "─" * line_length + f"{'─┘' if is_last else '─┤'}"
        print(f"{prefix}{self.icon} {self.name}{postfix}")

    def max_length(self, indent_length=0):
        return indent_length + len(f"{self.icon} {self.name}")


class ComponentVisitor:
    def visit_container(self, container):
        raise NotImplementedError

    def visit_leaf(self, leaf):
        raise NotImplementedError


class DrawVisitor(ComponentVisitor):
    def visit_container(self, container, indent="r", is_last=True):
        container.draw(indent, is_last)
        iterator = container.create_iterator()

    def visit_leaf(self, leaf, indent, is_last):
        leaf.draw(indent, is_last)


class StyleFactory:
    def create_container(self, name, icon):
        raise NotImplementedError

    def create_leaf(self, name, icon):
        raise NotImplementedError


class TreeStyleFactory(StyleFactory):
    def create_container(self, name, icon):
        return TreeContainer(name, icon)

    def create_leaf(self, name, icon):
        return TreeLeaf(name, icon)


class RectangleStyleFactory(StyleFactory):
    def create_container(self, name, icon):
        return RectangleContainer(name, icon)

    def create_leaf(self, name, icon):
        return RectangleLeaf(name, icon)


class IconFamily:
    def __init__(self, container_icon, leaf_icon):
        self.container_icon = container_icon
        self.leaf_icon = leaf_icon

    def get_container_icon(self):
        return self.container_icon

    def get_leaf_icon(self):
        return self.leaf_icon
