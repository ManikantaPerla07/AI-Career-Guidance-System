document.getElementById("predictBtn").addEventListener("click", async () => {

  const aptitudes = {
    linguistic: Number(linguisticVal.innerText),
    musical: Number(musicalVal.innerText),
    bodily: Number(bodilyVal.innerText),
    logical_mathematical: Number(logicalVal.innerText),
    spatial_visualization: Number(spatialVal.innerText),
    interpersonal: Number(interpersonalVal.innerText),
    intrapersonal: Number(intrapersonalVal.innerText),
    naturalist: Number(naturalistVal.innerText),
  };

  const getRadio = name =>
    document.querySelector(`input[name="${name}"]:checked`).value;

  const performance = {
    project_performance: getRadio("project_performance"),
    practical_skills: getRadio("practical_skills"),
    research_interest: getRadio("research_interest"),
    communication_skills: getRadio("communication_skills"),
    leadership_qualities: getRadio("leadership_qualities"),
    teamwork: getRadio("teamwork"),
    time_management: getRadio("time_management"),
    self_learning: getRadio("self_learning"),
  };

  try {
    const res = await fetch("http://127.0.0.1:5000/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ aptitudes, performance })
    });

    const data = await res.json();

    const list = document.getElementById("resultsList");
    list.innerHTML = "";

    data.top_predictions.forEach(item => {
      list.innerHTML += `
        <div class="bg-gray-800 p-5 rounded-xl shadow">
          <h4 class="text-xl font-bold text-indigo-400">
            #${item.rank} ${item.career}
          </h4>
          <p class="mt-2">Confidence:
            <span class="font-semibold">${item.confidence}%</span>
          </p>
        </div>`;
    });

    document.getElementById("resultBox").classList.remove("hidden");
    document.getElementById("resultBox")
  .scrollIntoView({ behavior: "smooth" });


  } catch (err) {
    alert("Backend not reachable. Start Flask server.");
  }
});
