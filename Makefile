all: hopper.xml cartpole.xml

hopper.xml: hopper.xml.rb
	ruby gen_xml.rb hopper.xml.rb > hopper.xml

cartpole.xml: cartpole.xml.rb
	ruby gen_xml.rb cartpole.xml.rb > cartpole.xml

test_cartpole:
	python cartpole.py

clean:
	rm *.xml
