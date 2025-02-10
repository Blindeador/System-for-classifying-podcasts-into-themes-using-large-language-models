// spotifyService.js
const axios = require('axios');
const https = require('https');
const { clientId, clientSecret } = require('../config');
const tokenStore = require('../tokenStore');  // Importamos el archivo de almacenamiento de tokens

// Crear el agente https
const agent = new https.Agent({
  rejectUnauthorized: false,
});

const getAccessToken = async () => {
  let accessToken = tokenStore.getAccessToken();  // Obtener el accessToken desde tokenStore

  if (!accessToken) {
    console.log('No hay token de acceso, solicitando uno nuevo...');
    await refreshAccessToken(); // Si no hay token, solicitamos uno nuevo
    accessToken = tokenStore.getAccessToken(); // Obtener el token actualizado
  }

  return accessToken;
};

const refreshAccessToken = async () => {
  const refreshToken = tokenStore.getRefreshToken(); // Obtener el refreshToken desde tokenStore

  if (!refreshToken) {
    throw new Error('No se puede refrescar el token: No hay refresh token disponible.');
  }

  try {
    const response = await axios.post(
      'https://accounts.spotify.com/api/token',
      new URLSearchParams({
        grant_type: 'refresh_token',
        refresh_token: refreshToken,
      }),
      {
        headers: {
          Authorization: 'Basic ' + Buffer.from(`${clientId}:${clientSecret}`).toString('base64'),
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        httpsAgent: agent,  // Usamos el httpsAgent
      }
    );

    // Verificamos que recibimos un nuevo access_token
    if (response.data.access_token) {
        // Actualizar el accessToken en tokenStore
        tokenStore.setAccessToken(response.data.access_token);
        console.log('Token actualizado exitosamente');
      } else {
        console.log('Error: No se recibió un nuevo access_token');
        throw new Error('No se pudo obtener el nuevo access_token');
      }
  } catch (error) {
    console.error('Error al refrescar el token:', error.message);
    throw new Error('No se pudo refrescar el token.');
  }
};

const searchPodcasts = async (query) => {
  const token = await getAccessToken();  // Obtenemos el token de acceso

  try {
    const response = await axios.get(`https://api.spotify.com/v1/search?q=${query}&type=show`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      httpsAgent: agent,  // Usamos el httpsAgent
    });

    return response.data.shows.items;
  } catch (error) {
    console.error('Error buscando podcasts:', error.message);
    throw new Error('Error al buscar podcasts.');
  }
};

module.exports = { searchPodcasts };
