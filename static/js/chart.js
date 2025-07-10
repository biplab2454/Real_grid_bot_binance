
fetch('/config')
.then(res => res.json())
.then(data => {
    const ctx = document.getElementById('gridChart').getContext('2d');
    const gridLevels = parseInt(data.grid_levels || 10);
    const values = Array.from({length: gridLevels}, (_, i) => i + 1);
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: values.map(v => 'Level ' + v),
            datasets: [{
                label: 'Grid Orders',
                data: values.map(v => Math.random() * 100),
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
            }]
        }
    });
});
