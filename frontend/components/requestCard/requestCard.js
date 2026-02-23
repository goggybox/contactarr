
// -----------------------------contactarr------------------------------
// This file is part of contactarr
// Copyright (C) 2025 goggybox https://github.com/goggybox

// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// that this program is licensed under. See LICENSE file. If not
// available, see <https://www.gnu.org/licenses/>.

// Please keep this header comment in all copies of the program.
// --------------------------------------------------------------------


/*
<div class="request-card" style="--backdrop-url: url('https://image.tmdb.org/t/p/w600_and_h900_bestv2/k2eK05xbqbILLUb0ag152auT0R5.jpg');">
  <div class="request-card-content">
    <div class="request-card-text">
      <a href="https://req.t1n.xyz/tv/43032" class="request-title" target="_blank" rel="noreferrer noopener">
        You're Under Arrest! (1996)
      </a>
      <div class="request-details">
        <span><strong>Requested By:</strong> Renee</span>
        <span><strong>Requested Seasons:</strong> 0, 1, 2, 3</span>
        <span class="request-timestamp">22:36:25 GMT+0000 (UTC)</span>
      </div>
    </div>
    <div class="request-card-poster">
      <a href="https://req.t1n.xyz/tv/43032" target="_blank" rel="noreferrer noopener">
        <img src="https://image.tmdb.org/t/p/w600_and_h900_bestv2/k2eK05xbqbILLUb0ag152auT0R5.jpg" alt="Poster">
      </a>
    </div>
  </div>
</div>
*/

function cr(type, clss, id) {
    const elem = document.createElement(type);
    if (clss) { elem.classList.add(clss); }
    if (id) { elem.id = id; }
    return elem;
}

function formatTimestamp(timestamp) {
    const date = new Date(timestamp * 1000);
    const hours = String(date.getUTCHours()).padStart(2, '0');
    const minutes = String(date.getUTCMinutes()).padStart(2, '0');
    const seconds = String(date.getUTCSeconds()).padStart(2, '0');
    return `${hours}:${minutes}:${seconds}`;
}

export function requestCard(request) {
    const request_card = cr("div", "request-card");
    // TODO: request_card.style.setProperty("--backdrop-url");
    
    request_card.innerHTML = `
        <div class="request-card-content">
            <div class="request-card-text">
                <a class="request-title">${request["name"]}</a>
                <div class="request-details">
                    <span><strong>Requested By:</strong> ${request["requested_by"]}</span>
                    ${request["type"] === "movie" ? `` : `<span><strong>Requested Seasons:</strong>${request["season_number"]}</span`}
                    <span class="request-timestamp>${formatTimestamp(request["requested_at"])}</span>
                </div>
            </div>
            <div class="request-card-poster">
                <a></a>
            </div>
        </div>
    `
}