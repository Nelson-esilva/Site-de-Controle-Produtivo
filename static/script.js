document.getElementById('chart-form').addEventListener('submit', function(event) {
    event.preventDefault();
    
    const colunasSelect = document.getElementById('colunas');
    const selectedColumns = Array.from(colunasSelect.selectedOptions).map(option => option.value);
    const graphTypeSelect = document.getElementById('tipo_grafico');
    const graphType = graphTypeSelect.value;

    fetch('/data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            selected_columns: selectedColumns,
            graph_type: graphType
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Erro ao obter os dados do servidor.');
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            throw new Error(data.error);
        }

        const ctx = document.getElementById('myChart').getContext('2d');
        if (window.myChart) {
            window.myChart.destroy();
        }
        
        let chartData;
        if (graphType === 'pie') {
            chartData = {
                labels: data.data[selectedColumns[0]],
                datasets: [{
                    label: selectedColumns[1],
                    data: data.data[selectedColumns[1]],
                    backgroundColor: data.data[selectedColumns[0]].map((_, idx) => `rgba(${idx * 50}, ${idx * 100}, ${idx * 150}, 0.2)`),
                    borderColor: data.data[selectedColumns[0]].map((_, idx) => `rgba(${idx * 50}, ${idx * 100}, ${idx * 150}, 1)`),
                    borderWidth: 1
                }]
            };
        } else {
            chartData = {
                labels: data.data[selectedColumns[0]],
                datasets: selectedColumns.slice(1).map((col, idx) => ({
                    label: col,
                    data: data.data[col],
                    backgroundColor: `rgba(${idx * 50}, ${idx * 100}, ${idx * 150}, 0.2)`,
                    borderColor: `rgba(${idx * 50}, ${idx * 100}, ${idx * 150}, 1)`,
                    borderWidth: 1
                }))
            };
        }

        const chartOptions = {
            type: graphType,
            data: chartData,
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        };

        if (graphType === 'pie') {
            delete chartOptions.options.scales;
        }

        window.myChart = new Chart(ctx, chartOptions);
    })
    .catch(error => {
        console.error('Erro ao processar requisição:', error);
        alert('Erro ao gerar o gráfico. Verifique sua conexão ou tente novamente mais tarde.');
    });
});
