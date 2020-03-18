import jsonlines
import json
class Obj(dict):
    def __init__(self, name, age):
        dict.__init__(self, name=name, age=age)


obj1 = Obj('haha', 123)
obj2 = Obj('3123', "sdasd")
obj3 = Obj([1,"dsad"], {123:"dsad"})
with jsonlines.open('output.jsonl', mode='w') as writer:
    writer.write(obj1)
    writer.write(obj2)
    writer.write_all([obj2, obj3])