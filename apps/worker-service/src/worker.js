"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var dotenv_1 = require("dotenv");
dotenv_1.default.config();
console.log('Worker Service starting...');
// Basic health check server
var express_1 = require("express");
var app = (0, express_1.default)();
var PORT = process.env.PORT || 3002;
app.get('/health', function (req, res) {
    res.json({ status: 'healthy', service: 'worker' });
});
app.listen(PORT, function () {
    console.log("Worker Service health endpoint on port ".concat(PORT));
});
// RabbitMQ consumer logic will go here
