import anywidget
import traitlets


class TableWidget(anywidget.AnyWidget):
    _esm = """
    function render({ model, el }) {
      let domElement = document.createElement("div");
      let innerHTML;
      el.classList.add("custom-table");
      let selectedIndex = -1; // Add a variable to keep track of the selected row index
      function drawTable() {
          const data = model.get("data");
          // clean up the dom element
          domElement.innerHTML = "";
          innerHTML = '<table><tr>' + data[0].map(header => `<th>${header}</th>`).join('') + '</tr>';
          for (let i = 1; i < data.length; i++) {
            innerHTML += '<tr>' + data[i].map(cell => `<td>${cell}</td>`).join('') + '</tr>';
          }
          innerHTML += "</table>"
          domElement.innerHTML += innerHTML
          // Adding click event listeners to each row
          const rows = domElement.querySelectorAll('tr');
          rows.forEach((row, index) => {
              // Skip the header row
              if (index > 0) {
                  row.addEventListener('click', () => {
                      // Remove selected class from previously selected row if any
                      if (selectedIndex >= 0 && rows[selectedIndex + 1]) {
                          rows[selectedIndex + 1].classList.remove('selected-row');
                      }
                      // Adjusted to match Python's 0-based indexing, subtract 1 to account for header
                      model.set('row_index', index - 1);
                      model.save_changes();
                      // Add selected class to the newly selected row
                      row.classList.add('selected-row');
                      selectedIndex = index - 1; // Update the selectedIndex
                  });
              }
          });
      }
      drawTable();
      domElement.addEventListener("row_click", () => {
        model.set("row_index", 1);
        model.save_changes();
      });
      model.on("change:data", () => {
        drawTable()
      });
      el.appendChild(domElement);
    }
    export default { render };
    """
    _css = """
    .custom-table table, .custom-table th, .custom-table td {
        border: 1px solid black;
        border-collapse: collapse;
        text-align: left;
        padding: 8px;
    }
    .custom-table th, .custom-table td {
        min-width: 60px;
        word-wrap: break-word;
    }
    .custom-table table {
        width: 100%;
        font-size: 1.2em;
    }
    /* hover effect */
    .custom-table tr:not(:first-child):hover, .custom-table tr.selected-row { /* Add .selected-row for persisting the background color */
        background-color: #FF474D; /* Light red background on hover and on selected row */
    }
    """
    data = traitlets.List().tag(sync=True)
    row_index = traitlets.Int().tag(sync=True)
