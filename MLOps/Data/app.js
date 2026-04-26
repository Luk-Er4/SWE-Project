async function loadChart() {
  const status = document.getElementById("status");

  try {
    // 1. 건강정보 API 먼저 호출
    const healthResponse = await fetch("http://127.0.0.1:8000/api/bring/user_health_info");

    if (!healthResponse.ok) {
      throw new Error("Failed to load user health data");
    }

    const healthData = await healthResponse.json();

    // 2. healthData를 chart API body 형태로 변환
    const chartBody = {
      user_name: healthData.user_name,
      sleep_hours: healthData.sleep,
      physical_activity: healthData.activity,
      diet_calories: healthData.diet,
      health_risk: healthData.stress_level,
      health_score: healthData.health_score
    };

    // 3. chart API 호출
    const chartResponse = await fetch("http://127.0.0.1:8000/api/user/comparison-chart", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(chartBody)
    });

    if (!chartResponse.ok) {
      throw new Error("Failed to load comparison chart");
    }

    const result = await chartResponse.json();

    // 4. summary 표시
    document.getElementById("summary").innerHTML = result.summary
      .map(item => `<p>• ${item.message}</p>`)
      .join("");

    // 5. Plotly 그래프 렌더링
    Plotly.newPlot(
      "chart",
      result.figure.data,
      result.figure.layout,
      { responsive: true }
    );

    status.innerHTML = "Chart loaded.";

  } catch (error) {
    console.error(error);
    status.innerHTML = "Error: " + error.message;
  }
}

loadChart();