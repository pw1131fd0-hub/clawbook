const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3003;
const DIARY_DIR = path.join(__dirname, 'frontend/build');
const API_TARGET = 'http://localhost:8000';

const mimeTypes = {
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.json': 'application/json',
    '.md': 'text/markdown'
};

const server = http.createServer((req, res) => {
    // Proxy API requests to backend
    if (req.url.startsWith('/api/')) {
        const options = {
            hostname: 'localhost',
            port: 8000,
            path: req.url,
            method: req.method,
            headers: req.headers
        };
        
        const proxyReq = http.request(options, (proxyRes) => {
            res.writeHead(proxyRes.statusCode, proxyRes.headers);
            proxyRes.pipe(res);
        });
        
        req.pipe(proxyReq);
        return;
    }
    
    let filePath = req.url === '/' ? '/index.html' : req.url;
    filePath = path.join(DIARY_DIR, filePath);
    
    const ext = path.extname(filePath);
    const contentType = mimeTypes[ext] || 'text/plain';
    
    fs.readFile(filePath, (err, content) => {
        if (err) {
            if (err.code === 'ENOENT') {
                // For React Router - serve index.html for non-file routes
                const indexPath = path.join(DIARY_DIR, 'index.html');
                fs.readFile(indexPath, (indexErr, indexContent) => {
                    if (indexErr) {
                        res.writeHead(404, { 'Content-Type': 'text/plain' });
                        res.end('404 Not Found');
                    } else {
                        res.writeHead(200, { 'Content-Type': 'text/html' });
                        res.end(indexContent);
                    }
                });
            } else {
                res.writeHead(500);
                res.end('Server Error');
            }
        } else {
            res.writeHead(200, { 'Content-Type': contentType });
            res.end(content);
        }
    });
});

server.listen(PORT, () => {
    console.log(`🦞 Diary server running at http://localhost:${PORT}`);
});
