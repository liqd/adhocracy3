test:
	pybot ./unit

init-headless:
	sudo nohup Xvfb :100 > /dev/null 2>&1 &

test-headless:
	DISPLAY=:100 make test

clean:
	rm -f selenium-screenshot-*.png report.html log.html output.xml
	find . -name '*~' -exec rm {} \;
