import { createRouter, createWebHistory } from "vue-router";
import CompanyList from "@/views/CompanyList.vue";
import CompanyAnalysis from "@/views/CompanyAnalysis.vue";
import Dashboard from "@/views/Dashboard.vue"; // Import the new Dashboard component

const routes = [
  {
    path: "/",
    name: "Dashboard", // This is now the home page
    component: Dashboard,
  },
  {
    path: "/companies",
    name: "CompanyList",
    component: CompanyList,
  },
  {
    path: "/company/:symbol",
    name: "CompanyAnalysis",
    component: CompanyAnalysis,
    props: (route) => ({
      symbol: decodeURIComponent(route.params.symbol),
    }),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
