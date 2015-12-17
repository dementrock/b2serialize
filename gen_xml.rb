require 'pry'
require 'nokogiri'
require 'active_support/all'

class Array

  def _is_1d_vector?
    self.all?{|x| x.is_a? Numeric}
  end

  def _is_2d_vector?
    self.all?{|x| x.try(:_is_1d_vector?) }
  end

  def to_s
    if _is_2d_vector?
      self.map(&:to_s).join(";")
    elsif _is_1d_vector?
      self.map(&:to_s).join(",")
    else
      super
    end
  end

end

class Nokogiri::XML::Builder

  def capsule(options={})
    from = options.delete(:from)
    to = options.delete(:to)
    radius = options.delete(:radius)
    x1, y1 = from
    x2, y2 = to
    if (y1 - y2).abs < 1e-6
      dx = 0
      dy = radius
    else
      dx = radius * 1.0 / (((x1 - x2) / (y1 - y2)) ** 2 + 1) ** 0.5
      dy = (radius**2 - dx**2) ** 0.5
    end
    vertices = [
      [x1 + dx, y1 + dy],
      [x2 + dx, y2 + dy],
      [x2 - dx, y2 - dy],
      [x1 - dx, y1 - dy],
    ]
    fixture(options.merge(shape: :polygon, vertices: vertices))
    fixture(options.merge(shape: :circle, center: from, radius: radius))
    fixture(options.merge(shape: :circle, center: to, radius: radius))
  end

end

class Fixnum

  def deg
    self
  end

end

builder = Nokogiri::XML::Builder.new do
  eval(open('hopper.xml.rb').read)
end
puts builder.to_xml
