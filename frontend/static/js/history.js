document.addEventListener('DOMContentLoaded', async () => {
    const tbody = document.getElementById('historyBody');
    const emptyDiv = document.getElementById('historyEmpty');

    const res = await api.getHistory();
    if (!res.success || !res.data || res.data.length === 0) {
        emptyDiv.style.display = 'block';
        return;
    }

    emptyDiv.style.display = 'none';
    res.data.forEach(r => {
        const probClass = r.success_probability >= 70 ? 'high' : r.success_probability >= 40 ? 'medium' : 'low';
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${r.prediction_date}</td>
            <td>${r.target_gpa.toFixed(2)}</td>
            <td>${r.predicted_gpa.toFixed(2)}</td>
            <td><span class="probability ${probClass}">${r.success_probability.toFixed(1)}%</span></td>
            <td>${r.similar_student_count}</td>
        `;
        tbody.appendChild(tr);
    });
});
