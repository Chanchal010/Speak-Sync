/**
 * Password Hash Generator
 * Usage: node scripts/generate-password.js <password>
 * Example: node scripts/generate-password.js Chanchal@1311
 *
 * Run this from inside the gateway container on the server:
 *   docker exec -it speak-sync-gateway node /app/scripts/generate-password.js Chanchal@1311
 */

const argon2 = require('argon2');

const password = process.argv[2];

if (!password) {
  console.error('❌ Please provide a password as argument');
  console.error('   Usage: node generate-password.js <password>');
  process.exit(1);
}

async function generateHash() {
  try {
    const hash = await argon2.hash(password, {
      type: argon2.argon2id,
      memoryCost: 2 ** 16,  // 64MB
      timeCost: 3,
      parallelism: 1,
    });

    console.log('\n✅ Password hashed successfully!\n');
    console.log('Plain:  ', password);
    console.log('Hash:   ', hash);
    console.log('\n📋 Copy the hash above into your database.\n');
  } catch (err) {
    console.error('❌ Error generating hash:', err.message);
  }
}

generateHash();
