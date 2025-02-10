//Este archivo configura el servidor y carga las rutas.
const express = require('express');
const bodyParser = require('body-parser');
const authRoutes = require('./routes/authRoutes');
const podcastRoutes = require('./routes/podcastRoutes');

const app = express();
app.use(bodyParser.json());

// Rutas para autenticación y podcasts
app.use('/auth', authRoutes);
app.use('/podcasts', podcastRoutes);

const PORT = 8888;
app.listen(PORT, () => {
  console.log(`Servidor corriendo en http://localhost:${PORT}`);
});
