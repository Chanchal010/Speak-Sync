import { Router } from 'express';
import { userController } from '../../controllers/user.controller.js';
import { verifyInternalRequest } from '../../middleware/internal-auth.middleware.js';

const router = Router();

// Apply internal auth middleware to all routes
router.use(verifyInternalRequest);

// User CRUD routes
router.post('/', userController.createUser.bind(userController));
router.get('/:id', userController.getUserById.bind(userController));
router.get('/email/:email', userController.getUserByEmail.bind(userController));
router.put('/:id', userController.updateUser.bind(userController));
router.patch('/:id/refresh-token', userController.updateRefreshToken.bind(userController));
router.delete('/:id', userController.deleteUser.bind(userController));

export default router;
