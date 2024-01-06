const express = require('express');
const bodyParser = require('body-parser');
const app = express();
const port = 3000;
var headsCount = 0;

app.use(bodyParser.json()); // Parse JSON bodies

// Add this middleware for CORS
app.use((req, res, next) => {
    res.header('Access-Control-Allow-Origin', '*');
    res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
    next();
});

app.get('/number', (req, res) => {
    res.send(headsCount.toString());
    console.log("LOG: counter: ", headsCount);
});

app.post('/headsCount', (req, res) => {
    const clientNumber = req.body.headsCount; // Get the number from the client's request
    res.send('Number updated successfully');
    headsCount = clientNumber;
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});


