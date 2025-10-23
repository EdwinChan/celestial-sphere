# store['time_of_year'] and store['time_of_day'] are mean times; therefore, if
# the day is solar, the Sun moves along an analemma subject only to the effects
# of obliquity

# eccentricity can be implemented by replacing the two instances of
# store['time_of_year'] in calculations of the Sun's position by the Sun's true
# anomaly; the two instances of store['time_of_year'] in the coordinate
# transformations should be kept unchanged in order for time to remain mean
# time

import math
import numpy
import itertools
from matplotlib import pyplot
from matplotlib.widgets import Slider

def rotate_x(p, x):
  c, s = math.cos(p), math.sin(p)
  [x, y, z] = x
  return [x, y*c-z*s, y*s+z*c]

def rotate_y(p, x):
  c, s = math.cos(p), math.sin(p)
  [x, y, z] = x
  return [z*s+x*c, y, z*c-x*s]

def rotate_z(p, x):
  c, s = math.cos(p), math.sin(p)
  [x, y, z] = x
  return [x*c-y*s, x*s+y*c, z]

def make_meridian(p, n=100):
  q = numpy.linspace(-math.pi, math.pi, n+1)
  return [
    numpy.sin(q) * math.cos(p),
    numpy.sin(q) * math.sin(p),
    numpy.cos(q)]

def make_parallel(q, n=100):
  p = numpy.linspace(-math.pi, math.pi, n+1)
  return [
    math.sin(q) * numpy.cos(p),
    math.sin(q) * numpy.sin(p),
    math.cos(q) * numpy.ones_like(p)]

def make_globe(i, j, n=100):
  assert i >= 0 and j >= 0
  result = []
  for q in numpy.linspace(0, math.pi, i*2+1)[1:-1]:
    result.append(make_parallel(q))
  for p in numpy.linspace(0, math.pi, j*2+1)[:-1]:
    result.append(make_meridian(p))
  return result

def demo():
  pyplot.figure()
  axes = pyplot.gcf().add_axes([0, 4/20, 1, 15/20], projection='3d')

  view_type_iter = itertools.cycle(['ecliptic', 'equator', 'horizon'])
  day_type_iter  = itertools.cycle(['sidereal', 'solar'])

  store = axes.store = {
    'artists':      [],
    'controls':     [],
    'obliquity':    math.pi/180 * 23.4392811,
    'latitude':     math.pi/180 * 40,
    'time_of_year': 0,
    'time_of_day':  0,
    'view_type':    next(view_type_iter),
    'day_type':     next(day_type_iter)}

  def transform_observer_to_inertial(x):
    colatitude = math.pi/2 - store['latitude']
    x = rotate_y(colatitude, x)
    x = rotate_z(store['time_of_day'], x)
    if store['day_type'] == 'solar':
      x = rotate_z(store['time_of_year'], x)
    return x

  def transform_inertial_to_ecliptic(x):
    x = rotate_y(store['obliquity'], x)
    return x

  def transform_ecliptic_to_view(x):
    if store['view_type'] == 'ecliptic':
      return x
    colatitude = math.pi/2 - store['latitude']
    x = rotate_y(-store['obliquity'], x)
    if store['view_type'] == 'equator':
      return x
    x = rotate_z(-store['time_of_day'], x)
    if store['day_type'] == 'solar':
      x = rotate_z(-store['time_of_year'], x)
    x = rotate_y(-colatitude, x)
    if store['view_type'] == 'horizon':
      return x

  def refresh(**kwargs):
    store.update(kwargs)
    artists = iter(store['artists']) if store['artists'] else None

    def plot(data, **prop):
      if not artists:
        artist, = axes.plot([], [], [], **prop)
        store['artists'].append(artist)
      else:
        artist = next(artists)
      data = transform_ecliptic_to_view(data)
      artist.set_data_3d(*data)

    def text(string, position, **prop):
      if not artists:
        prop = {**dict(ha='center', va='center'), **prop}
        artist = axes.text([], [], [], None, **prop)
        store['artists'].append(artist)
      else:
        artist = next(artists)
      position = transform_ecliptic_to_view(position)
      artist.set_text(string)
      artist.set_position_3d(position)

    def text2d(string, position, **prop):
      if not artists:
        prop = {**dict(transform=axes.figure.transFigure), **prop}
        artist = axes.text2D([], [], None, **prop)
        store['artists'].append(artist)
      else:
        artist = next(artists)
      artist.set_text(string)
      artist.set_position(position)

    # equatorial coordinate system
    for i, x in enumerate(make_globe(3, 3)):
      x = transform_inertial_to_ecliptic(x)
      plot(x, label='RA/Dec' if i == 0 else None, color='black', alpha=0.05)
    for s, x in {
        '+90\xb0':      [ 0,  0,  1],
        '\u221290\xb0': [ 0,  0, -1],
        '0h':           [ 0, -1,  0],
        '6h':           [ 1,  0,  0],
        '12h':          [ 0,  1,  0],
        '18h':          [-1,  0,  0]}.items():
      x = transform_inertial_to_ecliptic(x)
      text(s, x)

    # ecliptic
    x = make_parallel(math.pi/2)
    plot(x, label='ecliptic', color='red', alpha=0.2)

    # sun path
    x = make_parallel(math.acos(
      math.cos(store['time_of_year']) *
      math.sin(store['obliquity'])))
    x = transform_inertial_to_ecliptic(x)
    plot(x, color='red')

    # Sun
    x = [1, 0, 0]
    x = rotate_z(store['time_of_year'], x)
    plot(x, label='sun path', color='red', marker='o')

    # horizon
    x = make_parallel(math.pi/2)
    x = transform_observer_to_inertial(x)
    x = transform_inertial_to_ecliptic(x)
    plot(x, label='horizon', color='blue', alpha=0.2)

    # zenith
    x = numpy.transpose([[0, 0, 0], [0, 0, 1]])
    x = transform_observer_to_inertial(x)
    x = transform_inertial_to_ecliptic(x)
    plot(x, color='blue', alpha=0.2)
    for s, x in {
        'N': [-1,  0, 0],
        'E': [ 0,  1, 0],
        'S': [ 1,  0, 0],
        'W': [ 0, -1, 0]}.items():
      x = transform_observer_to_inertial(x)
      x = transform_inertial_to_ecliptic(x)
      text(s, x)
    x = make_parallel(math.pi/2 - store['latitude'])
    x = transform_inertial_to_ecliptic(x)
    plot(x, color='blue')
    x = [0, 0, 1]
    x = transform_observer_to_inertial(x)
    x = transform_inertial_to_ecliptic(x)
    plot(x, label='zenith', color='blue', marker='x')

    text2d(
      f'view: {store["view_type"]} (press 1 to cycle)\n'
      f'day: {store["day_type"]} (press 2 to cycle)',
      [0.02, 0.98], ha='left', va='top')

  refresh()
  pyplot.figlegend(loc='lower right', bbox_to_anchor=[0.98, 4/20+0.02])
  axes.set_xlim(-0.6, 0.6)
  axes.set_ylim(-0.6, 0.6)
  axes.set_zlim(-0.6, 0.6)
  axes.set_box_aspect([1, 1, 1])
  axes.view_init(10, -90, 0)
  axes.set_axis_off()

  control = Slider(
    pyplot.gcf().add_axes([1/8, 2/20, 1/4, 1/20]),
    label='obliquity',
    valmin=0, valmax=math.pi, valinit=store['obliquity'])
  control.on_changed(lambda value: refresh(obliquity=value))
  store['controls'].append(control)

  control = Slider(
    pyplot.gcf().add_axes([1/8, 1/20, 1/4, 1/20]),
    label='latitude',
    valmin=-math.pi/2, valmax=math.pi/2, valinit=store['latitude'])
  control.on_changed(lambda value: refresh(latitude=value))
  store['controls'].append(control)

  control = Slider(
    pyplot.gcf().add_axes([5/8, 2/20, 1/4, 1/20]),
    label='time of year',
    valmin=-math.pi, valmax=math.pi, valinit=store['time_of_year'])
  control.on_changed(lambda value: refresh(time_of_year=value))
  store['controls'].append(control)

  control = Slider(
    pyplot.gcf().add_axes([5/8, 1/20, 1/4, 1/20]),
    label='time of day',
    valmin=-math.pi, valmax=math.pi, valinit=store['time_of_day'])
  control.on_changed(lambda value: refresh(time_of_day=value))
  store['controls'].append(control)

  def on_key_press(event):
    if event.key == '1':
      refresh(view_type=next(view_type_iter))
      pyplot.draw()
    elif event.key == '2':
      refresh(day_type=next(day_type_iter))
      pyplot.draw()

  pyplot.connect('key_press_event', on_key_press)

if __name__ == '__main__':
  demo()
  pyplot.show()
