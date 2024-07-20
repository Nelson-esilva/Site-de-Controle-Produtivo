// Adiciona um listener para o evento de submit do formulário com id 'chart-form'
document.getElementById('chart-form').addEventListener('submit', function(event) {
    // Prevê o comportamento padrão do formulário, que é enviar a requisição e recarregar a página
    event.preventDefault();
    
    // Obtém a seleção de colunas do formulário
    const colunasSelect = document.getElementById('colunas');
    // Cria um array com os valores das opções selecionadas
    const selectedColumns = Array.from(colunasSelect.selectedOptions).map(option => option.value);
    // Obtém o tipo de gráfico selecionado
    const graphTypeSelect = document.getElementById('tipo_grafico');
    const graphType = graphTypeSelect.value;

    // Faz uma requisição POST para o endpoint '/data'
    fetch('/data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json' // Define o tipo de conteúdo como JSON
        },
        body: JSON.stringify({
            selected_columns: selectedColumns, // Dados das colunas selecionadas
            graph_type: graphType // Tipo de gráfico selecionado
        })
    })
    .then(response => {
        // Verifica se a resposta foi bem sucedida
        if (!response.ok) {
            throw new Error('Erro ao obter os dados do servidor.'); // Lança um erro se a resposta não for OK
        }
        return response.json(); // Converte a resposta para JSON
    })
    .then(data => {
        // Verifica se há um erro nos dados recebidos
        if (data.error) {
            throw new Error(data.error); // Lança um erro se houver uma mensagem de erro nos dados
        }

        // Obtém o contexto do canvas para o gráfico
        const ctx = document.getElementById('myChart').getContext('2d');
        // Destrói o gráfico existente (se houver) antes de criar um novo
        if (window.myChart) {
            window.myChart.destroy();
        }
        
        // Prepara os dados do gráfico com base no tipo selecionado
        let chartData;
        if (graphType === 'pie') {
            // Se o tipo de gráfico for 'pie'
            chartData = {
                labels: data.data[selectedColumns[0]], // Rótulos para o gráfico de pizza
                datasets: [{
                    label: selectedColumns[1], // Rótulo da série de dados
                    data: data.data[selectedColumns[1]], // Dados da série de dados
                    backgroundColor: data.data[selectedColumns[0]].map((_, idx) => `rgba(${idx * 50}, ${idx * 100}, ${idx * 150}, 0.2)`), // Cores de fundo das fatias
                    borderColor: data.data[selectedColumns[0]].map((_, idx) => `rgba(${idx * 50}, ${idx * 100}, ${idx * 150}, 1)`), // Cores da borda das fatias
                    borderWidth: 1 // Largura da borda das fatias
                }]
            };
        } else {
            // Para outros tipos de gráficos (como barras, linhas, etc.)
            chartData = {
                labels: data.data[selectedColumns[0]], // Rótulos para os eixos
                datasets: selectedColumns.slice(1).map((col, idx) => ({
                    label: col, // Rótulo da série de dados
                    data: data.data[col], // Dados da série de dados
                    backgroundColor: `rgba(${idx * 50}, ${idx * 100}, ${idx * 150}, 0.2)`, // Cor de fundo dos dados
                    borderColor: `rgba(${idx * 50}, ${idx * 100}, ${idx * 150}, 1)`, // Cor da borda dos dados
                    borderWidth: 1 // Largura da borda dos dados
                }))
            };
        }

        // Configura as opções do gráfico
        const chartOptions = {
            type: graphType, // Tipo de gráfico (pizza, barra, linha, etc.)
            data: chartData, // Dados do gráfico
            options: {
                scales: {
                    y: {
                        beginAtZero: true // Configura o eixo y para começar em zero
                    }
                }
            }
        };

        // Remove as opções de escala para gráficos de pizza
        if (graphType === 'pie') {
            delete chartOptions.options.scales;
        }

        // Cria um novo gráfico usando o Chart.js
        window.myChart = new Chart(ctx, chartOptions);
    })
    .catch(error => {
        // Trata erros que ocorrem durante o processo
        console.error('Erro ao processar requisição:', error);
        // Exibe uma mensagem de alerta para o usuário
        alert('Erro ao gerar o gráfico. Verifique sua conexão ou tente novamente mais tarde.');
    });
});
