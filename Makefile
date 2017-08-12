test:
	python3 tests/run.py
clean:
	rm -rf __pycache__ custom_prompt_types/__pycache__ ||:

.PHONY: clean test coldchain-cleanup

coldchain-cleanup:
	rm -rf /home/niles/Documents/odk/app-designer/app/config/assets/formgen
	rm /home/niles/Documents/odk/app-designer/app/config/assets/form_generator.js
	rm /home/niles/Documents/odk/app-designer/app/config/assets/form_generator.css
	rm /home/niles/Documents/odk/app-designer/app/config/assets/graph.html
	rm /home/niles/Documents/odk/app-designer/app/config/assets/detail.html
	rm /home/niles/Documents/odk/app-designer/app/config/assets/table.html
	rm /home/niles/Documents/odk/app-designer/app/config/assets/tables.html
