document.addEventListener('DOMContentLoaded', async () => {
    const profileDiv = document.getElementById('profileData');
    const predictionForm = document.getElementById('predictionForm');
    const resultDiv = document.getElementById('predictionResult');
    const todayDiv = document.getElementById('todayPrediction');
    const errorDiv = document.getElementById('predictionError');

    const profileRes = await api.getProfile();
    if (!profileRes.success) {
        profileDiv.innerHTML = '<div class="empty-state"><p>Profile not found. Please contact admin.</p></div>';
        return;
    }

    const p = profileRes.data;
    const isPending = p.student_code === 'PENDING' || (p.previous_cgpa || 0) === 0;

    profileDiv.innerHTML = `
        <div class="profile-grid">
            <div class="profile-item"><div class="label">Student Code</div><div class="value">${p.student_code}</div></div>
            <div class="profile-item"><div class="label">Full Name</div><div class="value">${p.full_name}</div></div>
            <div class="profile-item"><div class="label">Gender</div><div class="value">${p.gender || '-'}</div></div>
            <div class="profile-item"><div class="label">Age</div><div class="value">${p.age || '-'}</div></div>
            <div class="profile-item"><div class="label">Major</div><div class="value">${p.major || '-'}</div></div>
            <div class="profile-item"><div class="label">Attendance %</div><div class="value">${p.attendance_percentage || '-'}</div></div>
            <div class="profile-item"><div class="label">Study Hours/Day</div><div class="value">${p.study_hours_per_day || '-'}</div></div>
            <div class="profile-item"><div class="label">Sleep Hours/Day</div><div class="value">${p.sleep_hours_per_day || '-'}</div></div>
            <div class="profile-item"><div class="label">Social Hours/Week</div><div class="value">${p.social_hours_per_week || '-'}</div></div>
            <div class="profile-item"><div class="label">Previous CGPA</div><div class="value">${p.previous_cgpa || '-'}</div></div>
        </div>
    `;

    if (isPending) {
        predictionForm.style.display = 'none';
        resultDiv.innerHTML = '<div class="alert alert-warning">Your profile is incomplete. Please ask Admin to update your profile.</div>';
        return;
    }

    const todayRes = await api.getTodayPrediction();
    if (todayRes.success && todayRes.data) {
        predictionForm.style.display = 'none';
        const d = todayRes.data;
        const probClass = d.success_probability >= 70 ? 'high' : d.success_probability >= 40 ? 'medium' : 'low';
        resultDiv.innerHTML = `
            <div class="prediction-result">
                <div class="big-number">${d.predicted_gpa.toFixed(2)}</div>
                <div class="label">Predicted GPA</div>
                <div class="probability ${probClass}">${d.success_probability.toFixed(1)}% chance to reach ${d.target_gpa.toFixed(2)}</div>
                <div class="label">Based on ${d.similar_student_count} similar students</div>
                <div class="label" style="margin-top:.5rem">Prediction made on ${d.prediction_date}</div>
            </div>
        `;
    }

    predictionForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const targetGpa = parseFloat(document.getElementById('targetGpa').value);
        errorDiv.style.display = 'none';

        if (targetGpa <= 0 || targetGpa > 4.0) {
            errorDiv.textContent = 'Target GPA must be between 0 and 4.0';
            errorDiv.style.display = 'block';
            return;
        }

        const btn = predictionForm.querySelector('button');
        btn.disabled = true;
        btn.textContent = 'Predicting...';

        const res = await api.createPrediction(targetGpa);
        btn.disabled = false;
        btn.textContent = 'Predict';

        if (res.success) {
            predictionForm.style.display = 'none';
            const d = res.data;
            const probClass = d.success_probability >= 70 ? 'high' : d.success_probability >= 40 ? 'medium' : 'low';
            resultDiv.innerHTML = `
                <div class="prediction-result">
                    <div class="big-number">${d.predicted_gpa.toFixed(2)}</div>
                    <div class="label">Predicted GPA</div>
                    <div class="probability ${probClass}">${d.success_probability.toFixed(1)}% chance to reach ${d.target_gpa.toFixed(2)}</div>
                    <div class="label">Based on ${d.similar_student_count} similar students</div>
                </div>
            `;
        } else {
            errorDiv.textContent = res.message || res.detail?.message || 'Prediction failed';
            errorDiv.style.display = 'block';
        }
    });
});
