# def decorator(func):
#   def wrapper():
#     print('Decorator ran')
#     return func
#   return wrapper()
# @decorator
# def sayHi():
#   print('hi')


# sayHi()

# def decorator(func):
#   def wrapper():
#     print('hi from the decorator')
#     func()
#   return wrapper


# @decorator
# def sayHi():
#   print('hi from sayHi')

# sayHi()


def skewer(func):
  def wrapper(*args, **kwargs):
    func(*args,**kwargs)
    print('butthole!')
  return wrapper

@skewer
def sayThis(thing):
  print(thing)

sayThis('Hello!')