import argparse
import json
from components import TreeStyleFactory, RectangleStyleFactory, IconFamily, DrawVisitor

class TreeBuilder:
    def __init__(self, style_factory, icon_family):
        self.style_factory = style_factory
        self.icon_family = icon_family
        self.root = None

    def build_tree(self, data, name='root'):
        if isinstance(data, dict):
            node = self.style_factory.create_container(name, self.icon_family.get_container_icon())
            if self.root is None:
                self.root = node
            for key, value in data.items():
                child = self.build_tree(value, key)
                node.add_child(child)
            return node
        else:
            return self.style_factory.create_leaf(name + (": " + str(data) if data is not None else ""),
                                                  self.icon_family.get_leaf_icon())

    def get_result(self):
        return self.root


class FunnyJsonExplorer:
    def __init__(self, builder):
        self.builder = builder
        self.data = None

    def _load(self, filepath):
        with open(filepath, 'r') as f:
            self.data = json.load(f)

    def show(self, filepath):
        self._load(filepath)
        self.builder.build_tree(self.data)
        root = self.builder.get_result()
        draw_visitor = DrawVisitor()
        root.accept(draw_visitor)  # 使用访问者来处理绘制


def load_icon_families(config_file='icon_config.json'):
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)

    icon_families = {'default': IconFamily('', '')}  # 默认无标签族情况
    for family, icons in config.items():
        icon_families[family] = IconFamily(icons['container_icon'], icons['leaf_icon'])

    return icon_families


def main():
    parser = argparse.ArgumentParser(description="Funny JSON Explorer")
    parser.add_argument('-f', '--file', required=True, help='JSON file to be explored')
    parser.add_argument('-s', '--style', default='tree', help='Display style')
    parser.add_argument('-i', '--icon', default='default', help='Icon family')
    args = parser.parse_args()

    icon_families = load_icon_families("icon_config.json")  # 读入配置文件

    style_factories = {
        'tree': TreeStyleFactory(),
        'rectangle': RectangleStyleFactory()
    }

    builder = TreeBuilder(style_factories[args.style], icon_families[args.icon])
    explorer = FunnyJsonExplorer(builder)
    explorer.show(args.file)

if __name__ == "__main__":
    main()
