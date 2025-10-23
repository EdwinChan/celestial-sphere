import math
import numpy
from matplotlib import pyplot
from matplotlib.widgets import Slider

earth_obliquity   = math.pi/180 * 23.4392811

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

def get_sun_declination(o, t):
  return math.asin(math.cos(t)*math.sin(o))

def make_sun_path(o, t, l):
  d = get_sun_declination(o, t)
  return rotate_y(math.pi/2-l, make_parallel(math.pi/2-d))

def make_sun_path(o, t, l):
  d = get_sun_declination(o, t)
  p = numpy.linspace(-math.pi, math.pi, 101)
  return [
     math.sin(l)*math.cos(d)*numpy.cos(p) + math.cos(l)*math.sin(d),
                 math.cos(d)*numpy.sin(p),
    -math.cos(l)*math.cos(d)*numpy.cos(p) + math.sin(l)*math.sin(d)]

def plot_sun_paths():
  pyplot.figure()
  axes = pyplot.gcf().add_axes([0, 3/20, 1, 16/20], projection='3d')

  store = axes.store = {
    'artists':   [],
    'controls':  [],
    'obliquity': earth_obliquity,
    'latitude':  math.pi/180 * 40}

  def refresh(**kwargs):
    store.update(kwargs)
    artists = iter(store['artists']) if store['artists'] else None

    def plot(data, **prop):
      if not artists:
        artist, = axes.plot([], [], [], **prop)
        store['artists'].append(artist)
      else:
        artist = next(artists)
      artist.set_data_3d(*data)

    plot(
      make_sun_path(store['obliquity'], 0, store['latitude']),
      color='red', label='June solstice')
    plot(
      make_sun_path(store['obliquity'], math.pi/2, store['latitude']),
      color='green', label='equinoxes')
    plot(
      make_sun_path(store['obliquity'], math.pi, store['latitude']),
      color='blue', label='December solstice')

  for x in make_globe(3, 3):
    axes.plot(*x, color='black', alpha=0.05)
  for s, x in {
      'N': [ 1,  0, 0],
      'E': [ 0, -1, 0],
      'S': [-1,  0, 0],
      'W': [ 0,  1, 0],
      'Z': [ 0,  0, 1]}.items():
    axes.text(*x, s, ha='center', va='center')

  refresh()
  pyplot.figlegend(loc='lower right', bbox_to_anchor=[0.98, 3/20+0.02])
  axes.set_xlim(-0.6, 0.6)
  axes.set_ylim(-0.6, 0.6)
  axes.set_zlim(-0.6, 0.6)
  axes.set_box_aspect([1, 1, 1])
  axes.view_init(10, -90, 0)
  axes.set_axis_off()

  control = Slider(
    pyplot.gcf().add_axes([1/8, 1/20, 1/4, 1/20]),
    label='obliquity',
    valmin=0, valmax=math.pi, valinit=store['obliquity'])
  control.on_changed(lambda value: refresh(obliquity=value))
  store['controls'].append(control)

  control = Slider(
    pyplot.gcf().add_axes([5/8, 1/20, 1/4, 1/20]),
    label='latitude',
    valmin=-math.pi/2, valmax=math.pi/2, valinit=store['latitude'])
  control.on_changed(lambda value: refresh(latitude=value))
  store['controls'].append(control)

def plot_insolation_variation():
  pyplot.figure()

  t = numpy.linspace(-math.pi, math.pi, 361)
  d = numpy.vectorize(get_sun_declination)(earth_obliquity, t)
  for l in numpy.linspace(0, math.pi/2, 7)[:-1]:
    temp = numpy.clip(numpy.tan(l)*numpy.tan(d), -1, 1)
    temp = 1 - numpy.arccos(temp)/math.pi
    pyplot.plot(t/(2*math.pi), temp)

  pyplot.title('annual variation of insolation for different latitudes')
  pyplot.xlabel('fraction of tropical year from June solstice')
  pyplot.ylabel('sunlit fraction of solar day')

def plot_sunrise_position_variation():
  pyplot.figure()

  t = numpy.linspace(-math.pi, math.pi, 361)
  d = numpy.vectorize(get_sun_declination)(earth_obliquity, t)
  for l in numpy.linspace(0, math.pi/2, 7)[:-1]:
    temp = numpy.clip(numpy.tan(l)*numpy.tan(d), -1, 1)
    temp = numpy.arctan2(
      numpy.sqrt(1-temp**2),
      math.sin(l)*temp + math.cos(l)*numpy.tan(d))
    pyplot.plot(t/(2*math.pi), temp)

  pyplot.title('annual motion of the sunrise position for different latitudes')
  pyplot.xlabel('fraction of tropical year from June solstice')
  pyplot.ylabel('azimuth of sunrise (clockwise angle from north)')

if __name__ == '__main__':
  plot_sun_paths()
  plot_insolation_variation()
  plot_sunrise_position_variation()
  pyplot.show()
