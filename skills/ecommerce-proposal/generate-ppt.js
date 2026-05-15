/**
 * Autonomous Proposal PPT Generator
 * 
 * Generates branded PowerPoint presentations following Autonomous brand guide.
 * 
 * Usage:
 *   node generate-ppt.js --data proposal-data.json --output proposal.pptx
 *   
 * Or import and use programmatically:
 *   const { generateProposalPPT } = require('./generate-ppt.js');
 *   await generateProposalPPT(data, 'output.pptx');
 */

const pptxgen = require('pptxgenjs');
const fs = require('fs');
const path = require('path');

// ============================================
// AUTONOMOUS BRAND COLORS
// ============================================
const BRAND = {
  // Primary
  bgPrimary: '0a0a12',      // Dark background
  deepBlue: '151795',        // Hero gradients
  blue: '006aff',            // Primary buttons
  cyan: '00d5ff',            // Highlights, accents
  white: 'ffffff',           // Headings, text
  
  // Accent
  purple: '8c18c5',          // Gradient endpoints
  brightPurple: 'b42aff',    // Gradient endpoints
  midGray: '94a3b8',         // Body text
  
  // Cards
  cardBg: '12121a',          // Slightly lighter than bg
  cardBorder: '2a2a3a',      // Subtle border
};

// ============================================
// SLIDE TEMPLATES
// ============================================

function addCoverSlide(pptx, data) {
  const slide = pptx.addSlide();
  slide.background = { color: BRAND.bgPrimary };
  
  // Logo text (AUTONOMOUS)
  slide.addText('AUTONOMOUS', {
    x: 0, y: 1.8, w: '100%', h: 0.6,
    fontSize: 24,
    fontFace: 'Arial',
    bold: true,
    color: BRAND.cyan,
    align: 'center',
    charSpacing: 12,
  });
  
  // Main title
  slide.addText(data.title || 'Proposal', {
    x: 0.5, y: 2.6, w: 9, h: 1.2,
    fontSize: 36,
    fontFace: 'Arial',
    bold: true,
    color: BRAND.white,
    align: 'center',
    valign: 'middle',
  });
  
  // Subtitle
  slide.addText(data.subtitle || 'Ecommerce Development Proposal', {
    x: 0.5, y: 3.8, w: 9, h: 0.5,
    fontSize: 18,
    fontFace: 'Arial',
    color: BRAND.midGray,
    align: 'center',
  });
  
  // Client & Date
  slide.addText(`Prepared for: ${data.client || 'Client'}`, {
    x: 0.5, y: 4.6, w: 9, h: 0.4,
    fontSize: 14,
    fontFace: 'Arial',
    color: BRAND.white,
    align: 'center',
  });
  
  slide.addText(data.date || new Date().toLocaleDateString('en-US', { month: 'long', year: 'numeric' }), {
    x: 0.5, y: 5.0, w: 9, h: 0.4,
    fontSize: 12,
    fontFace: 'Arial',
    color: BRAND.midGray,
    align: 'center',
  });
}

function addSectionSlide(pptx, title) {
  const slide = pptx.addSlide();
  slide.background = { color: BRAND.bgPrimary };
  
  slide.addText(title, {
    x: 0.5, y: 2.3, w: 9, h: 1,
    fontSize: 40,
    fontFace: 'Arial',
    bold: true,
    color: BRAND.cyan,
    align: 'center',
    valign: 'middle',
  });
  
  // Underline accent
  slide.addShape(pptx.shapes.RECTANGLE, {
    x: 3.8, y: 3.4, w: 2.4, h: 0.06,
    fill: { color: BRAND.cyan },
  });
}

function addChallengeSlide(pptx, data) {
  const slide = pptx.addSlide();
  slide.background = { color: BRAND.bgPrimary };
  
  // Title
  slide.addText('The Challenge', {
    x: 0.6, y: 0.4, w: 8.8, h: 0.6,
    fontSize: 28,
    fontFace: 'Arial',
    bold: true,
    color: BRAND.cyan,
  });
  
  // Accent line
  slide.addShape(pptx.shapes.RECTANGLE, {
    x: 0.6, y: 1.0, w: 1.2, h: 0.05,
    fill: { color: BRAND.cyan },
  });
  
  // Intro text
  slide.addText(data.challengeIntro || 'Based on your requirements, here\'s what we understand:', {
    x: 0.6, y: 1.2, w: 8.8, h: 0.5,
    fontSize: 14,
    fontFace: 'Arial',
    color: BRAND.midGray,
  });
  
  // Challenge points
  const challenges = data.challenges || [];
  challenges.slice(0, 5).forEach((challenge, i) => {
    const y = 1.9 + (i * 0.85);
    
    // Card background
    slide.addShape(pptx.shapes.RECTANGLE, {
      x: 0.6, y: y, w: 8.8, h: 0.75,
      fill: { color: BRAND.cardBg },
      line: { color: BRAND.cardBorder, width: 0.5 },
    });
    
    // Cyan left border
    slide.addShape(pptx.shapes.RECTANGLE, {
      x: 0.6, y: y, w: 0.06, h: 0.75,
      fill: { color: BRAND.cyan },
    });
    
    // Text
    slide.addText(challenge, {
      x: 0.8, y: y + 0.15, w: 8.4, h: 0.5,
      fontSize: 13,
      fontFace: 'Arial',
      color: BRAND.white,
      valign: 'middle',
    });
  });
  
  addFooter(slide, pptx, 2);
}

function addApproachSlide(pptx, data) {
  const slide = pptx.addSlide();
  slide.background = { color: BRAND.bgPrimary };
  
  // Title
  slide.addText('Our Approach', {
    x: 0.6, y: 0.4, w: 8.8, h: 0.6,
    fontSize: 28,
    fontFace: 'Arial',
    bold: true,
    color: BRAND.cyan,
  });
  
  // Accent line
  slide.addShape(pptx.shapes.RECTANGLE, {
    x: 0.6, y: 1.0, w: 1.2, h: 0.05,
    fill: { color: BRAND.cyan },
  });
  
  // Steps
  const steps = data.approach || [];
  steps.slice(0, 4).forEach((step, i) => {
    const y = 1.4 + (i * 1.1);
    
    // Step number circle
    slide.addShape(pptx.shapes.OVAL, {
      x: 0.6, y: y, w: 0.5, h: 0.5,
      fill: { color: BRAND.deepBlue },
    });
    
    slide.addText((i + 1).toString(), {
      x: 0.6, y: y, w: 0.5, h: 0.5,
      fontSize: 16,
      fontFace: 'Arial',
      bold: true,
      color: BRAND.white,
      align: 'center',
      valign: 'middle',
    });
    
    // Step title
    slide.addText(step.title || `Step ${i + 1}`, {
      x: 1.3, y: y, w: 8.1, h: 0.4,
      fontSize: 15,
      fontFace: 'Arial',
      bold: true,
      color: BRAND.white,
    });
    
    // Step description
    slide.addText(step.description || '', {
      x: 1.3, y: y + 0.4, w: 8.1, h: 0.6,
      fontSize: 12,
      fontFace: 'Arial',
      color: BRAND.midGray,
    });
  });
  
  addFooter(slide, pptx, 3);
}

function addDeliverablesSlide(pptx, data) {
  const slide = pptx.addSlide();
  slide.background = { color: BRAND.bgPrimary };
  
  // Title
  slide.addText('What We\'ll Deliver', {
    x: 0.6, y: 0.4, w: 8.8, h: 0.6,
    fontSize: 28,
    fontFace: 'Arial',
    bold: true,
    color: BRAND.cyan,
  });
  
  // Accent line
  slide.addShape(pptx.shapes.RECTANGLE, {
    x: 0.6, y: 1.0, w: 1.2, h: 0.05,
    fill: { color: BRAND.cyan },
  });
  
  // 2x2 grid of deliverable cards
  const deliverables = data.deliverables || [];
  const positions = [
    { x: 0.6, y: 1.3 },
    { x: 5.0, y: 1.3 },
    { x: 0.6, y: 3.2 },
    { x: 5.0, y: 3.2 },
  ];
  
  deliverables.slice(0, 4).forEach((del, i) => {
    const pos = positions[i];
    
    // Card background
    slide.addShape(pptx.shapes.RECTANGLE, {
      x: pos.x, y: pos.y, w: 4.2, h: 1.7,
      fill: { color: BRAND.cardBg },
      line: { color: BRAND.cardBorder, width: 0.5 },
    });
    
    // Card title
    slide.addText(del.title || '', {
      x: pos.x + 0.2, y: pos.y + 0.15, w: 3.8, h: 0.35,
      fontSize: 14,
      fontFace: 'Arial',
      bold: true,
      color: BRAND.cyan,
    });
    
    // Card items
    const items = del.items || [];
    items.slice(0, 5).forEach((item, j) => {
      slide.addText(`→ ${item}`, {
        x: pos.x + 0.2, y: pos.y + 0.5 + (j * 0.22), w: 3.8, h: 0.22,
        fontSize: 10,
        fontFace: 'Arial',
        color: BRAND.midGray,
      });
    });
  });
  
  addFooter(slide, pptx, 4);
}

function addExperienceSlide(pptx, data) {
  const slide = pptx.addSlide();
  slide.background = { color: BRAND.bgPrimary };
  
  // Title
  slide.addText('Relevant Experience', {
    x: 0.6, y: 0.4, w: 8.8, h: 0.6,
    fontSize: 28,
    fontFace: 'Arial',
    bold: true,
    color: BRAND.cyan,
  });
  
  // Accent line
  slide.addShape(pptx.shapes.RECTANGLE, {
    x: 0.6, y: 1.0, w: 1.2, h: 0.05,
    fill: { color: BRAND.cyan },
  });
  
  // Case studies
  const cases = data.caseStudies || [];
  cases.slice(0, 2).forEach((cs, i) => {
    const y = 1.3 + (i * 2.0);
    
    // Card background
    slide.addShape(pptx.shapes.RECTANGLE, {
      x: 0.6, y: y, w: 8.8, h: 1.8,
      fill: { color: BRAND.cardBg },
      line: { color: BRAND.cardBorder, width: 0.5 },
    });
    
    // Title
    slide.addText(cs.title || '', {
      x: 0.8, y: y + 0.15, w: 8.4, h: 0.35,
      fontSize: 14,
      fontFace: 'Arial',
      bold: true,
      color: BRAND.cyan,
    });
    
    // Description
    slide.addText(cs.description || '', {
      x: 0.8, y: y + 0.5, w: 8.4, h: 0.35,
      fontSize: 11,
      fontFace: 'Arial',
      color: BRAND.midGray,
    });
    
    // Results
    const results = cs.results || [];
    results.slice(0, 4).forEach((result, j) => {
      slide.addText(`→ ${result}`, {
        x: 0.8, y: y + 0.9 + (j * 0.22), w: 8.4, h: 0.22,
        fontSize: 10,
        fontFace: 'Arial',
        color: BRAND.white,
      });
    });
  });
  
  addFooter(slide, pptx, 5);
}

function addWhyUsSlide(pptx, data) {
  const slide = pptx.addSlide();
  slide.background = { color: BRAND.bgPrimary };
  
  // Title
  slide.addText('Why Autonomous', {
    x: 0.6, y: 0.4, w: 8.8, h: 0.6,
    fontSize: 28,
    fontFace: 'Arial',
    bold: true,
    color: BRAND.cyan,
  });
  
  // Accent line
  slide.addShape(pptx.shapes.RECTANGLE, {
    x: 0.6, y: 1.0, w: 1.2, h: 0.05,
    fill: { color: BRAND.cyan },
  });
  
  // 2x3 grid of trust items
  const trustItems = data.whyUs || [
    { icon: '⚡', title: 'Fast Execution', desc: '2-3 week delivery on most projects.' },
    { icon: '🎯', title: 'Conversion-First', desc: 'Every decision drives revenue.' },
    { icon: '🔧', title: 'Full-Stack Team', desc: 'Design + Dev + Strategy in one.' },
    { icon: '📱', title: 'Mobile Excellence', desc: 'Optimized for real-world usage.' },
    { icon: '📊', title: 'Data-Driven', desc: 'Decisions backed by analytics.' },
    { icon: '🛡️', title: 'Quality Guaranteed', desc: 'Your success is our reputation.' },
  ];
  
  const positions = [
    { x: 0.6, y: 1.3 }, { x: 5.0, y: 1.3 },
    { x: 0.6, y: 2.6 }, { x: 5.0, y: 2.6 },
    { x: 0.6, y: 3.9 }, { x: 5.0, y: 3.9 },
  ];
  
  trustItems.slice(0, 6).forEach((item, i) => {
    const pos = positions[i];
    
    // Card
    slide.addShape(pptx.shapes.RECTANGLE, {
      x: pos.x, y: pos.y, w: 4.2, h: 1.1,
      fill: { color: BRAND.cardBg },
      line: { color: BRAND.cardBorder, width: 0.5 },
    });
    
    // Icon
    slide.addText(item.icon || '•', {
      x: pos.x + 0.15, y: pos.y + 0.2, w: 0.5, h: 0.5,
      fontSize: 24,
    });
    
    // Title
    slide.addText(item.title || '', {
      x: pos.x + 0.7, y: pos.y + 0.2, w: 3.3, h: 0.35,
      fontSize: 13,
      fontFace: 'Arial',
      bold: true,
      color: BRAND.white,
    });
    
    // Description
    slide.addText(item.desc || '', {
      x: pos.x + 0.7, y: pos.y + 0.55, w: 3.3, h: 0.4,
      fontSize: 10,
      fontFace: 'Arial',
      color: BRAND.midGray,
    });
  });
  
  addFooter(slide, pptx, 6);
}

function addNextStepsSlide(pptx, data) {
  const slide = pptx.addSlide();
  slide.background = { color: BRAND.bgPrimary };
  
  // Title
  slide.addText('Ready to Build?', {
    x: 0, y: 1.5, w: '100%', h: 0.7,
    fontSize: 36,
    fontFace: 'Arial',
    bold: true,
    color: BRAND.cyan,
    align: 'center',
  });
  
  // Subtitle
  slide.addText('Let\'s discuss your project and get started.', {
    x: 0, y: 2.2, w: '100%', h: 0.4,
    fontSize: 16,
    fontFace: 'Arial',
    color: BRAND.midGray,
    align: 'center',
  });
  
  // Contact card
  slide.addShape(pptx.shapes.RECTANGLE, {
    x: 2.8, y: 2.8, w: 4.4, h: 2.0,
    fill: { color: BRAND.cardBg },
    line: { color: BRAND.cardBorder, width: 0.5 },
  });
  
  // Email
  slide.addText('Email', {
    x: 2.8, y: 2.95, w: 4.4, h: 0.25,
    fontSize: 10,
    fontFace: 'Arial',
    color: BRAND.midGray,
    align: 'center',
  });
  slide.addText(data.email || 'hello@autonomous.mt', {
    x: 2.8, y: 3.2, w: 4.4, h: 0.3,
    fontSize: 14,
    fontFace: 'Arial',
    color: BRAND.cyan,
    align: 'center',
  });
  
  // Website
  slide.addText('Website', {
    x: 2.8, y: 3.6, w: 4.4, h: 0.25,
    fontSize: 10,
    fontFace: 'Arial',
    color: BRAND.midGray,
    align: 'center',
  });
  slide.addText(data.website || 'autonomous.mt', {
    x: 2.8, y: 3.85, w: 4.4, h: 0.3,
    fontSize: 14,
    fontFace: 'Arial',
    color: BRAND.cyan,
    align: 'center',
  });
  
  // Pricing
  if (data.price) {
    slide.addText(`Investment: ${data.price}`, {
      x: 2.8, y: 4.4, w: 4.4, h: 0.3,
      fontSize: 14,
      fontFace: 'Arial',
      bold: true,
      color: BRAND.white,
      align: 'center',
    });
  }
  
  if (data.timeline) {
    slide.addText(`Timeline: ${data.timeline}`, {
      x: 2.8, y: 4.7, w: 4.4, h: 0.25,
      fontSize: 11,
      fontFace: 'Arial',
      color: BRAND.midGray,
      align: 'center',
    });
  }
  
  addFooter(slide, pptx, 7);
}

function addFooter(slide, pptx, pageNum) {
  slide.addText('Autonomous', {
    x: 0.5, y: 5.2, w: 2, h: 0.3,
    fontSize: 9,
    fontFace: 'Arial',
    color: BRAND.midGray,
  });
  
  slide.addText(pageNum.toString(), {
    x: 9, y: 5.2, w: 0.5, h: 0.3,
    fontSize: 9,
    fontFace: 'Arial',
    color: BRAND.midGray,
    align: 'right',
  });
}

// ============================================
// MAIN GENERATOR FUNCTION
// ============================================

async function generateProposalPPT(data, outputPath) {
  const pptx = new pptxgen();
  
  // Presentation properties
  pptx.author = 'Autonomous';
  pptx.title = data.title || 'Proposal';
  pptx.subject = 'Ecommerce Development Proposal';
  pptx.company = 'Autonomous Technologies';
  
  // Slide size (16:9)
  pptx.defineLayout({ name: 'LAYOUT_16x9', width: 10, height: 5.625 });
  pptx.layout = 'LAYOUT_16x9';
  
  // Build slides
  addCoverSlide(pptx, data);
  addChallengeSlide(pptx, data);
  addApproachSlide(pptx, data);
  addDeliverablesSlide(pptx, data);
  addExperienceSlide(pptx, data);
  addWhyUsSlide(pptx, data);
  addNextStepsSlide(pptx, data);
  
  // Save
  await pptx.writeFile({ fileName: outputPath });
  console.log(`PPT generated: ${outputPath}`);
  return outputPath;
}

// ============================================
// CLI INTERFACE
// ============================================

if (require.main === module) {
  const args = process.argv.slice(2);
  const dataIdx = args.indexOf('--data');
  const outIdx = args.indexOf('--output');
  
  if (dataIdx === -1 || outIdx === -1) {
    console.log('Usage: node generate-ppt.js --data proposal-data.json --output proposal.pptx');
    process.exit(1);
  }
  
  const dataFile = args[dataIdx + 1];
  const outputFile = args[outIdx + 1];
  
  const data = JSON.parse(fs.readFileSync(dataFile, 'utf8'));
  generateProposalPPT(data, outputFile).catch(console.error);
}

module.exports = { generateProposalPPT, BRAND };
