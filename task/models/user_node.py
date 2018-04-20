from neomodel import StructuredNode, StringProperty


class UserNode(StructuredNode):
    uid = StringProperty(unique_index=True, required=True)
