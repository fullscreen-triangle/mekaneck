//! Ternary Operators: ENCODE, DECODE, TRISECT, NAVIGATE_TERNARY.
//!
//! Operators for ternary tree navigation.

use vb_core::error::TernaryAddrError;
use vb_core::types::{SCoord, TernaryAddr};

/// ENCODE operator: Integer to ternary address.
pub fn encode(value: u64, depth: usize) -> Result<TernaryAddr, TernaryAddrError> {
    TernaryAddr::encode(value, depth)
}

/// ENCODE_FLOAT operator: Float to ternary address.
pub fn encode_float(value: f64, depth: usize) -> Result<TernaryAddr, TernaryAddrError> {
    TernaryAddr::from_float(value, depth)
}

/// DECODE operator: Ternary address to integer.
pub fn decode(addr: &TernaryAddr) -> u64 {
    addr.decode()
}

/// DECODE_FLOAT operator: Ternary address to float.
pub fn decode_float(addr: &TernaryAddr) -> f64 {
    addr.to_float()
}

/// TRISECT operator: Split address into three children.
pub fn trisect(addr: &TernaryAddr) -> (TernaryAddr, TernaryAddr, TernaryAddr) {
    addr.trisect()
}

/// NAVIGATE_TERNARY operator: Path through ternary tree.
pub fn navigate_ternary(from: &TernaryAddr, to: &TernaryAddr) -> Vec<TernaryAddr> {
    from.path_to(to)
}

/// Ternary distance between addresses.
pub fn ternary_distance(addr1: &TernaryAddr, addr2: &TernaryAddr) -> usize {
    addr1.navigation_distance(addr2)
}

/// Encode SCoord as three ternary addresses.
pub fn encode_scoord(s: &SCoord, depth: usize) -> Result<(TernaryAddr, TernaryAddr, TernaryAddr), TernaryAddrError> {
    let sk_addr = TernaryAddr::from_float(s.sk, depth)?;
    let st_addr = TernaryAddr::from_float(s.st, depth)?;
    let se_addr = TernaryAddr::from_float(s.se, depth)?;
    Ok((sk_addr, st_addr, se_addr))
}

/// Decode three ternary addresses to SCoord.
pub fn decode_scoord(
    sk_addr: &TernaryAddr,
    st_addr: &TernaryAddr,
    se_addr: &TernaryAddr,
) -> SCoord {
    SCoord::new_unchecked(
        sk_addr.to_float(),
        st_addr.to_float(),
        se_addr.to_float(),
    )
}

/// Ternary search: Find value using trisection.
pub fn ternary_search<F>(
    target: f64,
    evaluate: F,
    depth: usize,
) -> TernaryAddr
where
    F: Fn(f64) -> f64,
{
    let mut addr = TernaryAddr::root();

    for _ in 0..depth {
        let (left, mid, right) = addr.trisect();

        let left_val = evaluate(left.to_float());
        let mid_val = evaluate(mid.to_float());
        let right_val = evaluate(right.to_float());

        let left_err = (left_val - target).abs();
        let mid_err = (mid_val - target).abs();
        let right_err = (right_val - target).abs();

        addr = if left_err <= mid_err && left_err <= right_err {
            left
        } else if mid_err <= right_err {
            mid
        } else {
            right
        };
    }

    addr
}

/// Ternary efficiency: log_2(3) ≈ 1.585 bits per trit.
pub fn ternary_efficiency() -> f64 {
    3.0_f64.log2()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_encode_decode() {
        for val in 0..27 {
            let addr = encode(val, 3).unwrap();
            assert_eq!(decode(&addr), val);
        }
    }

    #[test]
    fn test_float_roundtrip() {
        let values = [0.1, 0.25, 0.5, 0.75, 0.9];
        for &v in &values {
            let addr = encode_float(v, 8).unwrap();
            let decoded = decode_float(&addr);
            assert!((decoded - v).abs() < 0.01);
        }
    }

    #[test]
    fn test_trisect() {
        let root = TernaryAddr::root();
        let (l, m, r) = trisect(&root);
        assert_eq!(l.depth(), 1);
        assert_eq!(m.depth(), 1);
        assert_eq!(r.depth(), 1);
    }

    #[test]
    fn test_encode_decode_scoord() {
        let s = SCoord::new(0.3, 0.5, 0.7).unwrap();
        let (sk, st, se) = encode_scoord(&s, 8).unwrap();
        let decoded = decode_scoord(&sk, &st, &se);

        assert!((decoded.sk - s.sk).abs() < 0.01);
        assert!((decoded.st - s.st).abs() < 0.01);
        assert!((decoded.se - s.se).abs() < 0.01);
    }

    #[test]
    fn test_ternary_search() {
        let addr = ternary_search(0.5, |x| x, 10);
        let found = addr.to_float();
        assert!((found - 0.5).abs() < 0.01);
    }

    #[test]
    fn test_ternary_efficiency() {
        let eff = ternary_efficiency();
        assert!((eff - 1.585).abs() < 0.01);
    }
}
