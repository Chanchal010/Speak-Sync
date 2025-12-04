import express from 'express';
import { eventController } from '../controllers/event.controller.js';

const router = express.Router();

/**
 * Event Routes
 * Base path: /api/events
 */

// Create events
router.post('/', (req, res) => eventController.createEvent(req, res));
router.post('/recurring', (req, res) => eventController.createRecurringEvent(req, res));

// Read events
router.get('/', (req, res) => eventController.getEvents(req, res));
router.get('/stats', (req, res) => eventController.getEventStats(req, res));
router.get('/free-busy', (req, res) => eventController.getFreeBusy(req, res));
router.get('/:id', (req, res) => eventController.getEventById(req, res));

// Update events
router.put('/:id', (req, res) => eventController.updateEvent(req, res));

// Delete events
router.delete('/:id', (req, res) => eventController.deleteEvent(req, res));

// Utility operations
router.post('/conflicts', (req, res) => eventController.checkConflicts(req, res));
router.post('/bulk/delete', (req, res) => eventController.bulkDeleteEvents(req, res));

export default router;
