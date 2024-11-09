from typing import Dict, Union


class Block:
    def __init__(self, content: any = None, name: Union[None, str] = None,
                 attributes: Union[None, Dict[str, any]] = None, level: int = 1):
        self.name = name
        self.level = level

        # check empty values passed as argument
        if content is not None:
            if isinstance(content, str) and content.strip() == '':
                self.content = None
            else:
                self.content = str(content)

        if attributes is not None:
            if isinstance(attributes, dict) and attributes == {}:
                self.attributes = None
            else:
                self.attributes = attributes

    def __str__(self):
        string = f'{self.level * "-"}'

        if self.name is not None:
            string += f'|{self.name}'
        if self.attributes is not None:
            string += f'|{str(self.attributes)}'
        if self.content is not None:
            string += f'|{str(self.content)}'

        return string
