// The (dashboard) route group handles "/" — this file must not exist as a separate route.
// Re-export the dashboard overview page so only ONE page handles the root route.
export { default } from './(dashboard)/page';
