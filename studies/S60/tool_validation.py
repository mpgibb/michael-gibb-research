"""Side-effect-free validation for the bounded tool-call intervention."""
import ast,json,copy
from pathlib import Path
import jsonschema


def read_tool_schemas(directory:Path):
    """Read literal published schemas without importing or invoking benchmark tools."""
    schemas={}
    for path in sorted(directory.glob('*.py')):
        tree=ast.parse(path.read_text())
        for node in ast.walk(tree):
            if not isinstance(node,ast.FunctionDef) or node.name!='get_info':continue
            returns=[item for item in ast.walk(node) if isinstance(item,ast.Return)]
            if len(returns)!=1:raise ValueError('Tool schema is not a single literal return')
            definition=ast.literal_eval(returns[0].value);function=definition['function'];name=function['name']
            if name in schemas:raise ValueError('Duplicate tool name')
            schemas[name]=function['parameters']
    if not schemas:raise ValueError('No published tool schemas found')
    return schemas


def reject_constant(value):raise ValueError('Non-finite JSON numeric constant')


def unique_object(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError('Duplicate JSON argument key')
        result[key]=value
    return result


def validate_call(name,arguments,schemas):
    if name not in schemas:return {'valid':False,'reason':'unknown_tool','arguments':None}
    try:
        parsed=json.loads(arguments,parse_constant=reject_constant,object_pairs_hook=unique_object) if isinstance(arguments,str) else arguments
    except (ValueError,TypeError):return {'valid':False,'reason':'invalid_json','arguments':None}
    if not isinstance(parsed,dict):return {'valid':False,'reason':'non_object_arguments','arguments':None}
    schema=copy.deepcopy(schemas[name]);schema['additionalProperties']=False
    errors=list(jsonschema.Draft7Validator(schema).iter_errors(parsed))
    if errors:return {'valid':False,'reason':'schema_'+str(errors[0].validator),'arguments':None}
    return {'valid':True,'reason':None,'arguments':parsed}
