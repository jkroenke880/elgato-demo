var CATALOG = [
  {
    product_id: 'stream-deck-mk2',
    name: 'Stream Deck MK.2',
    price: 149.99,
    category: 'Stream Controllers',
    brand: 'Elgato',
    description: 'Take control of your content with 15 customizable LCD keys. Launch clips, switch scenes, adjust audio, tweet, and much more — all at the touch of a button. Fully customizable with the Stream Deck app.',
    sku: '10MUX01',
    image: null
  },
  {
    product_id: 'stream-deck-xl',
    name: 'Stream Deck XL',
    price: 249.99,
    category: 'Stream Controllers',
    brand: 'Elgato',
    description: '32 customizable LCD keys give you unrivaled control of your content. Trigger unlimited actions, switch scenes, launch media, adjust audio, and integrate with your entire ecosystem from one place.',
    sku: '10020419',
    image: null
  },
  {
    product_id: 'facecam-pro',
    name: 'Facecam Pro',
    price: 299.99,
    category: 'Cameras',
    brand: 'Elgato',
    description: 'The world\'s first 4K60 Ultra HD webcam for streaming. Sony STARVIS sensor, f/2.0 prime lens, DSLR-grade controls, and no compression — pure, unprocessed 4K60 straight to your stream or recording.',
    sku: '10WAA9901',
    image: null
  },
  {
    product_id: 'wave-3',
    name: 'Wave:3 USB Microphone',
    price: 149.99,
    category: 'Microphones',
    brand: 'Elgato',
    description: 'Premium studio-quality condenser microphone with 24-bit / 96 kHz audio, Clipguard technology, integrated pop filter, and Wave Link software for a complete broadcast-grade audio setup.',
    sku: '10MAB9901',
    image: null
  },
  {
    product_id: 'key-light',
    name: 'Key Light',
    price: 199.99,
    category: 'Lighting',
    brand: 'Elgato',
    description: 'Professional 2800-lumen studio lighting engineered for desk use. 80 LEDs, adjustable color temperature (2900–7000K), app-controlled brightness, and a durable aluminum build with an articulating arm.',
    sku: '10GAK9901',
    image: null
  },
  {
    product_id: '4k60-pro-mk2',
    name: '4K60 Pro MK.2 Capture Card',
    price: 199.99,
    category: 'Capture Cards',
    brand: 'Elgato',
    description: 'Capture and stream at 4K60 HDR10 with zero-lag passthrough. PCIe internal capture card supports VRR passthrough, instant gameview, and works seamlessly with OBS, Streamlabs, and XSplit.',
    sku: '10GBE9901',
    image: null
  }
];

function getProductById(id) {
  return CATALOG.find(function(p) { return p.product_id === id; });
}
