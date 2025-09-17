from graphql import parse, GraphQLError
from graphql.language.ast import FragmentDefinition, FragmentSpread

def detect_circular_fragments(query_str: str):
    """
    Parses the query and raises GraphQLError if circular fragments are found.
    Works with graphql-core==2.3.2
    """
    try:
        ast = parse(query_str)
    except Exception:
        return

    frag_deps = {}
    for definition in ast.definitions:
        if isinstance(definition, FragmentDefinition):
            name = definition.name.value
            spreads = [
                sel.name.value
                for sel in definition.selection_set.selections
                if isinstance(sel, FragmentSpread)
            ]
            frag_deps[name] = spreads

    visited = set()
    stack = set()
    def dfs(frag):
        if frag in stack:
            raise GraphQLError(f"Circular fragment detected: {frag}")
        if frag in visited:
            return
        visited.add(frag)
        stack.add(frag)
        for dep in frag_deps.get(frag, []):
            dfs(dep)
        stack.remove(frag)

    for f in frag_deps:
        dfs(f)