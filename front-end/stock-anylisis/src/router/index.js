import { createRouter, createWebHistory } from "vue-router";
import CompanyList from "@/views/CompanyList.vue";
import CompanyAnalysis from "@/views/CompanyAnalysis.vue";

const routes = [
  {
    path: "/",
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
