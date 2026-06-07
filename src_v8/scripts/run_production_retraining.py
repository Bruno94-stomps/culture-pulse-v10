#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 Production Retraining Orchestrator
Executa workflow completo de retreino com dados de produção

Workflow:
1. Coletar dados de produção estendidos (60-90 dias, 500-1000 samples)
2. Calibrar thresholds baseado em distribuição real
3. Aplicar thresholds calibrados
4. Validar Variant C vs Baseline A
5. Coletar ground truth (opcional - manual)
6. Re-treinar com ground truth (se disponível)
7. Gerar relatório final

Autor: Culture Pulse V9.1+
Data: Fevereiro 2026
"""

import sys
from pathlib import Path
import subprocess
import json
import logging
from datetime import datetime
from typing import Dict, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProductionRetrainingOrchestrator:
    """Orquestrador de retreino com dados de produção"""
    
    def __init__(self):
        """Inicializar orquestrador"""
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'steps': {},
            'summary': {}
        }
        logger.info("🎯 Production Retraining Orchestrator initialized")
    
    def run_step(self, step_name: str, command: List[str], critical: bool = True) -> bool:
        """
        Executar um passo do workflow
        
        Args:
            step_name: Nome do passo
            command: Comando a executar
            critical: Se True, falha interrompe workflow
        
        Returns:
            True se sucesso, False se falha
        """
        logger.info("\n" + "="*80)
        logger.info(f"▶️  STEP: {step_name}")
        logger.info("="*80)
        
        start_time = datetime.now()
        
        try:
            result = subprocess.run(
                command,
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=300  # 5 min timeout
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            success = result.returncode == 0
            
            self.results['steps'][step_name] = {
                'command': ' '.join(command),
                'duration_seconds': duration,
                'success': success,
                'return_code': result.returncode,
                'stdout_lines': len(result.stdout.splitlines()),
                'stderr_lines': len(result.stderr.splitlines())
            }
            
            if success:
                logger.info(f"✅ {step_name} completed in {duration:.1f}s")
                return True
            else:
                logger.error(f"❌ {step_name} failed (return code: {result.returncode})")
                logger.error(f"   stderr: {result.stderr[-500:]}")  # Last 500 chars
                
                if critical:
                    logger.error("   Critical step failed, stopping workflow")
                    return False
                else:
                    logger.warning("   Non-critical step failed, continuing...")
                    return True
        
        except subprocess.TimeoutExpired:
            logger.error(f"❌ {step_name} timed out after 5 minutes")
            self.results['steps'][step_name] = {
                'command': ' '.join(command),
                'success': False,
                'error': 'Timeout after 300s'
            }
            return False if critical else True
        
        except Exception as e:
            logger.error(f"❌ {step_name} raised exception: {e}")
            self.results['steps'][step_name] = {
                'command': ' '.join(command),
                'success': False,
                'error': str(e)
            }
            return False if critical else True
    
    def run_full_workflow(self, days: int = 90, min_samples: int = 1000):
        """Executar workflow completo"""
        logger.info("\n" + "="*80)
        logger.info("🎯 PRODUCTION RETRAINING WORKFLOW")
        logger.info("="*80)
        logger.info(f"Configuration:")
        logger.info(f"  Days: {days}")
        logger.info(f"  Min Samples: {min_samples}")
        
        # STEP 1: Coletar dados de produção
        if not self.run_step(
            "Collect Production Data",
            ["python", "scripts/collect_production_data.py", "--days", str(days), "--min-samples", str(min_samples)],
            critical=True
        ):
            return False
        
        # STEP 2: Calibrar thresholds
        if not self.run_step(
            "Calibrate Thresholds",
            ["python", "scripts/calibrate_thresholds.py"],
            critical=True
        ):
            return False
        
        # STEP 3: Validar Variant C
        if not self.run_step(
            "Validate Variant C",
            ["python", "scripts/validate_variant_c_production.py"],
            critical=False  # Não crítico, pode não haver weak signals
        ):
            pass
        
        # STEP 4: Verificar se há recommendation de threshold
        calibration_path = Path("results/threshold_calibration.json")
        if calibration_path.exists():
            with open(calibration_path, 'r', encoding='utf-8') as f:
                calibration = json.load(f)
            
            if 'recommended_strategy' in calibration:
                recommended = calibration['recommended_strategy']
                new_threshold = calibration['recommended_thresholds'][recommended]['threshold']
                
                logger.info("\n" + "="*80)
                logger.info("🎯 THRESHOLD RECOMMENDATION")
                logger.info("="*80)
                logger.info(f"Strategy: {recommended}")
                logger.info(f"New Threshold: {new_threshold:.3f}")
                logger.info("\nTo apply:")
                logger.info("  python scripts/update_thresholds.py")
        
        # STEP 5: Gerar relatório final
        self._generate_final_report()
        
        logger.info("\n" + "="*80)
        logger.info("✅ WORKFLOW COMPLETE")
        logger.info("="*80)
        
        return True
    
    def _generate_final_report(self):
        """Gerar relatório final do workflow"""
        logger.info("\n" + "="*80)
        logger.info("📊 FINAL REPORT")
        logger.info("="*80)
        
        # Estatísticas gerais
        total_steps = len(self.results['steps'])
        successful_steps = sum(1 for step in self.results['steps'].values() if step['success'])
        total_duration = sum(step.get('duration_seconds', 0) for step in self.results['steps'].values())
        
        self.results['summary'] = {
            'total_steps': total_steps,
            'successful_steps': successful_steps,
            'failed_steps': total_steps - successful_steps,
            'success_rate': successful_steps / total_steps if total_steps > 0 else 0,
            'total_duration_seconds': total_duration
        }
        
        logger.info(f"\nExecution Summary:")
        logger.info(f"  Total Steps: {total_steps}")
        logger.info(f"  Successful: {successful_steps} ({self.results['summary']['success_rate']:.1%})")
        logger.info(f"  Failed: {self.results['summary']['failed_steps']}")
        logger.info(f"  Total Duration: {total_duration:.1f}s")
        
        # Detalhes por step
        logger.info(f"\nStep Details:")
        for step_name, step_data in self.results['steps'].items():
            status = "✅" if step_data['success'] else "❌"
            duration = step_data.get('duration_seconds', 0)
            logger.info(f"  {status} {step_name}: {duration:.1f}s")
        
        # Carregar resultados individuais
        self._load_individual_results()
        
        # Salvar relatório
        report_path = Path("results/production_retraining_report.json")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n💾 Report saved to: {report_path}")
    
    def _load_individual_results(self):
        """Carregar resultados individuais dos scripts"""
        
        # Calibration
        calibration_path = Path("results/threshold_calibration.json")
        if calibration_path.exists():
            with open(calibration_path, 'r', encoding='utf-8') as f:
                calibration = json.load(f)
            
            self.results['calibration'] = {
                'current_threshold': calibration.get('current_threshold', 70.0),
                'recommended_strategy': calibration.get('recommended_strategy', 'N/A'),
                'distributions': calibration.get('distributions', {})
            }
            
            if 'recommended_strategy' in calibration:
                strategy = calibration['recommended_strategy']
                self.results['calibration']['recommended_threshold'] = calibration['recommended_thresholds'][strategy]['threshold']
            
            logger.info(f"\n📊 Calibration Results:")
            logger.info(f"  Current Threshold: {self.results['calibration']['current_threshold']:.1f}")
            logger.info(f"  Recommended: {self.results['calibration'].get('recommended_threshold', 'N/A')}")
        
        # Variant C Validation
        validation_path = Path("results/variant_c_production_validation.json")
        if validation_path.exists():
            with open(validation_path, 'r', encoding='utf-8') as f:
                validation = json.load(f)
            
            self.results['validation'] = {
                'baseline_f1': validation['baseline_a']['f1_score'],
                'variant_c_f1': validation['variant_c']['f1_score'],
                'comparison': validation['comparison']
            }
            
            logger.info(f"\n🧪 Validation Results:")
            logger.info(f"  Baseline A F1: {self.results['validation']['baseline_f1']:.4f}")
            logger.info(f"  Variant C F1: {self.results['validation']['variant_c_f1']:.4f}")


def main():
    """Main"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Production retraining workflow orchestrator')
    parser.add_argument('--days', type=int, default=90, help='Days to collect (max 90)')
    parser.add_argument('--min-samples', type=int, default=1000, help='Minimum samples target')
    args = parser.parse_args()
    
    orchestrator = ProductionRetrainingOrchestrator()
    success = orchestrator.run_full_workflow(days=args.days, min_samples=args.min_samples)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
