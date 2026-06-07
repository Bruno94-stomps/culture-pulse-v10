declare module "jspdf" {
  export class jsPDF {
    constructor(options?: any);
    setFillColor(...args: any[]): this;
    rect(...args: any[]): this;
    setTextColor(...args: any[]): this;
    setFontSize(...args: any[]): this;
    setFont(...args: any[]): this;
    text(...args: any[]): this;
    line(...args: any[]): this;
    save(...args: any[]): this;
    setDrawColor(...args: any[]): this;
    setPage(pageNumber: number): this;
    autoTable(options: any): this;
    internal: any;
  }
}

declare module "jspdf-autotable" {
  import { jsPDF } from "jspdf";
  export default function autoTable(this: jsPDF, options: any): jsPDF;
}
