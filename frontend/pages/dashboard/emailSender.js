
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

export async function sendIndividualEmailsWithProgress(subject, htmlBody, recipients, sender, callbacks = {}) {
    if (!recipients || recipients.length === 0) {
        throw new Error("No recipients provided");
    }
    
    if (!subject || !htmlBody || !sender) {
        throw new Error("Missing required fields: subject, htmlBody, or sender");
    }

    const { onStart, onProgress, onComplete, onError } = callbacks;
    
    const response = await fetch("/backend/smtp/send_email_stream", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            subject: subject,
            html_body: htmlBody,
            recipients: recipients,
            sender: sender
        })
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    let finalResult = null;

    // process SSE updates
    try {
        while (true) {
            const { done, value } = await reader.read();
            
            if (value) {
                buffer += decoder.decode(value, { stream: !done });
            }
            
            let lineEnd;
            while ((lineEnd = buffer.indexOf('\n')) !== -1) {
                const line = buffer.slice(0, lineEnd).trim();
                buffer = buffer.slice(lineEnd + 1);
                
                if (line.startsWith("data: ")) {
                    try {
                        const data = JSON.parse(line.slice(6));
                        console.log("Received SSE data:", data);
                        
                        switch (data.type) {
                            case 'start':
                                if (onStart) onStart(data);
                                break;
                            case 'progress':
                                if (onProgress) onProgress(data);
                                break;
                            case 'complete':
                                finalResult = data;
                                if (onComplete) onComplete(data);
                                return data;
                            case 'error':
                                if (onError) onError(data.message);
                                throw new Error(data.message);
                        }
                    } catch (e) {
                        console.error("Failed to parse SSE data:", line, e);
                    }
                }
            }
            
            if (done) break;
        }
    } finally {
        reader.releaseLock();
    }
    
    // should not happen, just in case
    if (!finalResult) {
        throw new Error("Stream ended without completion message");
    }
    
    return finalResult;
}

export function buildEmailHtml(contentHtml, footerHtml) {
    return `<!DOCTYPE html>
    <html>
    <head>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #1B1E23;
                color: #333;
                padding: 20px;
            }
            .email-container {
                max-width: 700px;
                margin: auto;
                background: #000000;
                padding: 0px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.05);
            }
            .content-container {
                padding: min(3vw,30px);
            }
            h2 {
                color: #EBAE00;
            }
            .btn {
                display: inline-block;
                margin-top: 20px;
                padding: 10px 20px;
                background: #EBAE00;
                color: white;
                text-decoration: none;
                border-radius: 5px;
            }
            img.banner {
                display: block;
                width: 100%;
                border-radius: 10px 10px 0 0;
                margin: 0 auto;
            }
            hr {
                color:#EBAE00;
                margin: 30px 0;
            }
            strong {
                color:#EBAE00;
            }
            p {
                color:white;
                font-size: 18px;
            }
            #quote {
                margin-left: 10px;
                padding-left: 10px;
                border-left: 2px solid #a7a7a7;
                color: #a7a7a7;
                font-style: italic;
            }
            .data-policy p, .data-policy strong {
                color:#BFBFBF;
            }
            .footer {
                border-top: 2px solid #555a61;
                padding: 5px 7px 5px 7px;
            }
            .footer p {
                color:#BFBFBF;
                text-align: center;
                font-size: 14px;
            }
            a {
                color: inherit;
            }
        </style>
    </head>
    <body>
        <div class="email-container">
            <img src="banner.png" alt="Banner" class="banner">
            <div class="content-container">
                ${contentHtml}
            </div>
            <div class="footer">
                <p>${footerHtml}</p>
            </div>
        </div>
    </body>
    </html>`;
}