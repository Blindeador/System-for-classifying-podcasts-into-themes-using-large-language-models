// tokenStore.js
let accessToken = '';
let refreshToken = '';

module.exports = {
  setAccessToken(token) {
    accessToken = token;
  },
  getAccessToken() {
    return accessToken;
  },
  setRefreshToken(token) {
    refreshToken = token;
  },
  getRefreshToken() {
    return refreshToken;
  },
};
