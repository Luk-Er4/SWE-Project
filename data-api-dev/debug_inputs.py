def form():
    return """
    <h2>Enter Your Info</h2>
    <form action="/predict" method="post">
        <input name="age" type="number" placeholder="Age"><br>
        <input name="gender" placeholder="Gender"><br>
        <label for='smoking'>smoking Status:</label>
        <select name="smoking" id="smoking">
        <option value="Never">Never</option>
        <option value="Low">Low</option>
        <option value="Medium">Medium</option>
        <option value="High">High</option>
        </select>
        <br>
        <input name="activity" type="number" placeholder="Activity"><br>
        <input name="sleep" type="number" placeholder="Sleep"><br>
        <input name="height" type="number" placeholder="Height"><br>
        <input name="weight" type="number" placeholder="Weight"><br>
        <input name="profession" placeholder="Profession"><br>
        <label for='education'>Education:</label>
        <select name="education" id="education">
        <option value="Highschool">Highschool</option>
        <option value="some college">some college</option>
        <option value="Bachlores">Bachlores</option>
        <option value="Masters">Masters</option>
        <option value="PHD">PHD</option>
        </select>
        <br>
        <input name="diet" type="number" placeholder="Diet"><br>
        <input name="diseases" type="number" placeholder="Diseases"><br>
        <input name="country" placeholder="Country"><br>

        <button type="submit">Submit</button>
    </form>
    """