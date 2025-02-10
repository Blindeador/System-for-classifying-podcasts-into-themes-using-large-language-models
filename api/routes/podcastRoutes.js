//Solicita podcasts a través de la API de Spotify.
const express = require('express');
const router = express.Router();
const spotifyService = require('../services/spotifyService');

router.get('/search', async (req, res) => {
  const query = req.query.q || 'technology';
  
  try {
    const podcasts = await spotifyService.searchPodcasts(query);
    res.json(podcasts);
  } catch (error) {
    console.error('Error buscando podcasts:', error.message);
    res.status(500).send('Error buscando podcasts.');
  }
});

module.exports = router;
