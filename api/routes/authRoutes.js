// authRoutes.js
const express = require('express');
const querystring = require('querystring');
const axios = require('axios');
const https = require('https');
const { clientId, clientSecret, redirectUri } = require('../config');
const tokenStore = require('../tokenStore'); // Importa el archivo de almacenamiento de tokens
const router = express.Router();
const agent = new https.Agent({
  rejectUnauthorized: false,
});

function generateRandomString(length) {
  const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += characters.charAt(Math.floor(Math.random() * characters.length));
  }
  return result;
}

// Ruta para iniciar sesión y redirigir al usuario a Spotify para la autorización
router.get('/login', (req, res) => {
  const state = generateRandomString(16);
  const scope = 'user-read-private user-read-email';

  const queryParams = querystring.stringify({
    response_type: 'code',
    client_id: clientId,
    scope: scope,
    redirect_uri: redirectUri,
    state: state,
  });

  res.redirect(`https://accounts.spotify.com/authorize?${queryParams}`);
});

// Ruta de callback de Spotify para recibir el código de autorización
router.get('/callback', async (req, res) => {
  const code = req.query.code || null;

  if (!code) {
    return res.send('Error: No authorization code received');
  }

  try {
    const response = await axios.post(
      'https://accounts.spotify.com/api/token',
      querystring.stringify({
        code: code,
        redirect_uri: redirectUri,
        grant_type: 'authorization_code',
      }),
      {
        headers: {
          Authorization: 'Basic ' + Buffer.from(`${clientId}:${clientSecret}`).toString('base64'),
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        httpsAgent: agent,
      }
    );

    // Log para revisar qué devuelve Spotify
    console.log('Respuesta de Spotify:', response.data);

    // Verificamos si el refresh_token está presente en la respuesta
    if (response.data.access_token && response.data.refresh_token) {
      // Almacenamos los tokens en tokenStore
      tokenStore.setAccessToken(response.data.access_token);
      tokenStore.setRefreshToken(response.data.refresh_token);
      res.send('¡Autenticación completada!');
    } else {
      console.log('No se obtuvo un refresh_token');
      res.status(400).send('Error: No se pudo obtener el refresh_token');
    }
  } catch (error) {
    console.error('Error intercambiando el código por el token:', error.message);
    res.status(500).send('Error en la autenticación.');
  }
});

// Ruta para refrescar el token
router.get('/refresh_token', async (req, res) => {
  const refreshToken = tokenStore.getRefreshToken(); // Obtener el refreshToken desde el tokenStore

  if (!refreshToken) {
    return res.status(400).send('No hay refresh token disponible');
  }

  try {
    const response = await axios.post(
      'https://accounts.spotify.com/api/token',
      querystring.stringify({
        grant_type: 'refresh_token',
        refresh_token: refreshToken,
      }),
      {
        headers: {
          Authorization: 'Basic ' + Buffer.from(`${clientId}:${clientSecret}`).toString('base64'),
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      }
    );

    // Almacenar el nuevo accessToken
    tokenStore.setAccessToken(response.data.access_token);

    res.json({ accessToken: response.data.access_token });
  } catch (error) {
    console.error('Error refrescando el token:', error.message);
    res.status(500).send('Error refrescando el token.');
  }
});

module.exports = router;
