import prisma from '../lib/prisma.js';
import { CategoryService } from '../services/category.service.js';

/**
 * Seed default categories for all existing users
 */
async function seedCategories() {
    console.log('🌱 Seeding default categories for existing users...');
    
    const categoryService = new CategoryService();
    
    try {
        // Get all users
        const users = await prisma.user.findMany({
            select: {
                id: true,
                email: true,
                name: true,
            },
        });
        
        console.log(`Found ${users.length} users`);
        
        for (const user of users) {
            try {
                // Check if user already has categories
                const existingCategories = await prisma.category.count({
                    where: { userId: user.id },
                });
                
                if (existingCategories > 0) {
                    console.log(`✓ User ${user.email} already has ${existingCategories} categories`);
                    continue;
                }
                
                // Create default categories
                await categoryService.createDefaultCategories(user.id);
                console.log(`✓ Created default categories for user: ${user.email}`);
            } catch (error) {
                console.error(`✗ Failed to create categories for user ${user.email}:`, error);
            }
        }
        
        console.log('✓ Category seeding completed!');
        
        // Display summary
        const totalCategories = await prisma.category.count();
        console.log(`\n📊 Total categories in database: ${totalCategories}`);
        
    } catch (error) {
        console.error('✗ Failed to seed categories:', error);
        throw error;
    } finally {
        await prisma.$disconnect();
    }
}

// Run seeding
seedCategories()
    .then(() => {
        console.log('Done!');
        process.exit(0);
    })
    .catch((error) => {
        console.error('Error:', error);
        process.exit(1);
    });
